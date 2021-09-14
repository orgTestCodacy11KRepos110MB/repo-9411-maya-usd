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
#include "editability.h"

#include <mayaUsd/base/tokens.h>

PXR_NAMESPACE_OPEN_SCOPE

/*! \brief  Verify if a property is locked.
 */
bool Editability::isLocked(UsdProperty property)
{
    // The reason we treat invalid property as editable is because we don't want
    // to influence editability of things that are not property that are being
    // tested by accident.
    if (!property.IsValid())
        return false;

    TfToken lock;
    if (!property.GetMetadata(MayaUsdMetadata->Lock, &lock))
        return false;

    if (lock == MayaUsdMetadata->Off) {
        return false;
    } else if (lock == MayaUsdMetadata->On) {
        return true;
    } else {
        TF_WARN(
            "Invalid token value [%s] for maya lock will be treated as [off].", lock.data());
        return false;
    }
}

PXR_NAMESPACE_CLOSE_SCOPE
