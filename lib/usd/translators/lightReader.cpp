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
#include <mayaUsd/fileio/primReaderRegistry.h>
#include <mayaUsd/fileio/translators/translatorLight.h>

#include <pxr/usd/usdLux/cylinderLight.h>
#include <pxr/usd/usdLux/diskLight.h>
#include <pxr/usd/usdLux/distantLight.h>
#include <pxr/usd/usdLux/domeLight.h>
#include <pxr/usd/usdLux/geometryLight.h>
#include <pxr/usd/usdLux/rectLight.h>
#include <pxr/usd/usdLux/sphereLight.h>
#include <pxr/usd/usdRi/pxrAovLight.h>
#include <pxr/usd/usdRi/pxrEnvDayLight.h>

PXR_NAMESPACE_OPEN_SCOPE

// Build variable used to import usd builtin
// lights as maya lights
#ifndef MAYA_USD_IMPORT_PXR_LIGHTS

PXRUSDMAYA_DEFINE_READER(UsdLuxDistantLight, args, context)
{
    return UsdMayaTranslatorLight::Read(args, context);
}

PXRUSDMAYA_DEFINE_READER(UsdLuxRectLight, args, context)
{
    return UsdMayaTranslatorLight::Read(args, context);
}

PXRUSDMAYA_DEFINE_READER(UsdLuxSphereLight, args, context)
{
    return UsdMayaTranslatorLight::Read(args, context);
}
#endif

PXR_NAMESPACE_CLOSE_SCOPE
