//
// Copyright 2019 Autodesk
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
#include "UsdObject3d.h"

#include <mayaUsd/ufe/UsdUndoVisibleCommand.h>
#include <mayaUsd/ufe/Utils.h>
#include <mayaUsd/utils/util.h>

#include <pxr/usd/usd/timeCode.h>
#include <pxr/usd/usdGeom/bboxCache.h>
#include <pxr/usd/usdGeom/tokens.h>
#include <pxr/usd/usdShade/materialBindingAPI.h>

#include <ufe/attributes.h>
#include <ufe/types.h>

#include <stdexcept>

PXR_NAMESPACE_USING_DIRECTIVE

namespace {
Ufe::Vector3d toVector3d(const GfVec3d& v) { return Ufe::Vector3d(v[0], v[1], v[2]); }
} // namespace

namespace MAYAUSD_NS_DEF {
namespace ufe {

UsdObject3d::UsdObject3d(const UsdSceneItem::Ptr& item)
    : Ufe::Object3d()
    , fItem(item)
    , fPrim(item->prim())
{
}

UsdObject3d::~UsdObject3d() { }

/*static*/
UsdObject3d::Ptr UsdObject3d::create(const UsdSceneItem::Ptr& item)
{
    return std::make_shared<UsdObject3d>(item);
}

//------------------------------------------------------------------------------
// Ufe::Object3d overrides
//------------------------------------------------------------------------------

Ufe::SceneItem::Ptr UsdObject3d::sceneItem() const { return fItem; }

Ufe::SceneItem::Ptr UsdObject3d::assignedMaterial() const
{
    PXR_NAMESPACE_USING_DIRECTIVE
    const UsdSceneItem::Ptr usdItem = std::dynamic_pointer_cast<UsdSceneItem>(fItem);
    if (!fItem || !TF_VERIFY(usdItem)) {
        return nullptr;
    }

    const PXR_NS::UsdPrim& prim = usdItem->prim();
    const PXR_NS::UsdShadeMaterialBindingAPI bindingApi(prim);
    const PXR_NS::UsdShadeMaterialBindingAPI::DirectBinding directBinding = bindingApi.GetDirectBinding();
    const PXR_NS::UsdShadeMaterial material = directBinding.GetMaterial();
    if (material) {
        const PXR_NS::UsdPrim& materialPrim = material.GetPrim();
        if (materialPrim) {
            const PXR_NS::SdfPath& materialSdfPath = materialPrim.GetPath();
            const Ufe::Path materialUfePath = usdPathToUfePathSegment(materialSdfPath);

            // Construct a UFE path consisting of two segments: 
            // 1. The path to the USD stage
            // 2. The path to our material
            const auto stagePathSegments    = usdItem->path().getSegments();
            const auto materialPathSegments = materialUfePath.getSegments();
            if (stagePathSegments.empty() || materialPathSegments.empty())
                return nullptr;
            const auto ufePath = Ufe::Path({stagePathSegments[0], materialPathSegments[0]});

            return UsdSceneItem::create(ufePath, materialPrim);
        }
    }
    return nullptr;
}

Ufe::BBox3d UsdObject3d::boundingBox() const
{
    // Use USD to compute the bounding box in local space.
    // UsdGeomBoundable::ComputeExtentFromPlugins() allows a plugin to register
    // an extent computation; this could be explored if needed in the future.
    //
    // Would be nice to know if the object extents are animated or not, so
    // we can bypass time computation and simply use UsdTimeCode::Default()
    // as the time.

    const auto& path = sceneItem()->path();
    auto        purposes = getProxyShapePurposes(path);
    // Add in the default purpose.
    purposes.emplace_back(UsdGeomTokens->default_);

    // UsdGeomImageable::ComputeUntransformedBound() just calls
    // UsdGeomBBoxCache, so do this here as well.
    auto time = getTime(path);
    auto bbox = UsdGeomBBoxCache(time, purposes).ComputeUntransformedBound(fPrim);

    // Add maya-specific extents
    UsdMayaUtil::AddMayaExtents(bbox, fPrim, time);

    auto range = bbox.ComputeAlignedRange();
    return Ufe::BBox3d(toVector3d(range.GetMin()), toVector3d(range.GetMax()));
}

bool UsdObject3d::visibility() const
{
    TfToken visibilityToken;
    auto    visAttr = UsdGeomImageable(fPrim).GetVisibilityAttr();
    visAttr.Get(&visibilityToken);

    return visibilityToken != UsdGeomTokens->invisible;
}

void UsdObject3d::setVisibility(bool vis)
{
    vis ? UsdGeomImageable(fPrim).MakeVisible() : UsdGeomImageable(fPrim).MakeInvisible();
}

Ufe::UndoableCommand::Ptr UsdObject3d::setVisibleCmd(bool vis)
{
    return UsdUndoVisibleCommand::create(fPrim, vis);
}

} // namespace ufe
} // namespace MAYAUSD_NS_DEF
