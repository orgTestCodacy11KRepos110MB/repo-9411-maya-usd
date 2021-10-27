//
// Copyright 2021 Autodesk
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
#include "UsdUIUfeObserver.h"

#include <pxr/base/tf/diagnostic.h>
#include <pxr/usd/usdGeom/tokens.h>

#include <maya/MGlobal.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <ufe/attributes.h>
#include <ufe/pathString.h>

// Needed because of TF_VERIFY
PXR_NAMESPACE_USING_DIRECTIVE

namespace MAYAUSD_NS_DEF {
namespace ufe {

//------------------------------------------------------------------------------
// Global variables
//------------------------------------------------------------------------------
Ufe::Observer::Ptr UsdUIUfeObserver::ufeObserver;

//------------------------------------------------------------------------------
// UsdUIUfeObserver
//------------------------------------------------------------------------------

UsdUIUfeObserver::UsdUIUfeObserver()
    : Ufe::Observer()
{
}

/*static*/
void UsdUIUfeObserver::create()
{
    TF_VERIFY(!ufeObserver);
    if (!ufeObserver) {
        ufeObserver = std::make_shared<UsdUIUfeObserver>();
        Ufe::Attributes::addObserver(ufeObserver);
    }
}

/*static*/
void UsdUIUfeObserver::destroy()
{
    TF_VERIFY(ufeObserver);
    if (ufeObserver) {
        Ufe::Attributes::removeObserver(ufeObserver);
        ufeObserver.reset();
    }
}

//------------------------------------------------------------------------------
// Ufe::Observer overrides
//------------------------------------------------------------------------------

void UsdUIUfeObserver::operator()(const Ufe::Notification& notification)
{
    if (auto ac = dynamic_cast<const Ufe::AttributeValueChanged*>(&notification)) {
        if (ac->name() == UsdGeomTokens->xformOpOrder) {
            static const MString mainObjListCmd(
                "if (`channelBox -exists mainChannelBox`) channelBox -q -mainObjectList "
                "mainChannelBox;");
            MStringArray paths;
            if (MGlobal::executeCommand(mainObjListCmd, paths) && (paths.length() > 0)) {
                // Under certain circumstances a USD attribute change causes
                // the xformOpOrder attribute to change while the channel box
                // is displaying a Maya object.  This Maya object is returned
                // without Maya path component separators (e.g. "Xform2"),
                // which triggers UFE single-segment path construction, but
                // there is none in Maya for any run-time, so an exception is
                // thrown and we crash.  Unconditionally refresh the channel
                // box for now.  PPT, 20-Oct-2021.
#ifdef SINGLE_SEGMENT_PATH_CRASH
                auto ufePath = Ufe::PathString::path(paths[0].asChar());
                if (ufePath.startsWith(ac->path())) {
#endif
                    static const MString updateCBCmd("channelBox -e -update mainChannelBox;");
                    MGlobal::executeCommand(updateCBCmd);
#ifdef SINGLE_SEGMENT_PATH_CRASH
                }
#endif
            }
        }
    }
}

} // namespace ufe
} // namespace MAYAUSD_NS_DEF
