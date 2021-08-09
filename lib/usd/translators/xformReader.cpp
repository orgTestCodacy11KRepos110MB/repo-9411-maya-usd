//
// Copyright 2016 Pixar
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
#include <mayaUsd/fileio/primReaderRegistry.h>
#include <mayaUsd/fileio/translators/translatorUtil.h>

#include <pxr/pxr.h>
#include <pxr/usd/usd/prim.h>

#include <maya/MObject.h>

PXR_NAMESPACE_OPEN_SCOPE

PXRUSDMAYA_DEFINE_READER(UsdGeomXform, args, context)
{
    const UsdPrim& usdPrim = args.GetUsdPrim();
    MObject        parentNode = context->GetMayaNode(usdPrim.GetPath().GetParentPath(), true);

    MStatus status;
    MObject mayaNode;
    return UsdMayaTranslatorUtil::CreateTransformNode(
        usdPrim, parentNode, args, context, &status, &mayaNode);
}

PXR_NAMESPACE_CLOSE_SCOPE
