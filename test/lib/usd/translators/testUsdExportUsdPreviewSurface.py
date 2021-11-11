#!/usr/bin/env mayapy
#
# Copyright 2020 Apple Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import unittest

import fixturesUtils
from maya import cmds
from maya import standalone

from pxr import Gf
from pxr import Sdf
from pxr import Usd
from pxr import UsdShade
from pxr import UsdUtils


class testUsdExportUsdPreviewSurface(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.input_dir = fixturesUtils.setUpClass(__file__)
        cls.temp_dir = os.path.abspath('.')

    @classmethod
    def tearDownClass(cls):
        standalone.uninitialize()

    def _GetUsdMaterial(self, stage, materialName):
        modelPrimPath = Sdf.Path.absoluteRootPath.AppendChild(
            'UsdPreviewSurfaceExportTest')
        materialsRootPrimPath = modelPrimPath.AppendChild(
            UsdUtils.GetMaterialsScopeName())
        materialPrimPath = materialsRootPrimPath.AppendChild(materialName)
        materialPrim = stage.GetPrimAtPath(materialPrimPath)
        self.assertTrue(materialPrim)

        materialSchema = UsdShade.Material(materialPrim)
        self.assertTrue(materialSchema)

        return materialSchema

    def _GetSourceShader(self, inputOrOutput):
        (connectableAPI, _, _) = inputOrOutput.GetConnectedSource()
        self.assertTrue(connectableAPI.GetPrim().IsA(UsdShade.Shader))
        shaderPrim = connectableAPI.GetPrim()
        self.assertTrue(shaderPrim)

        shader = UsdShade.Shader(shaderPrim)
        self.assertTrue(shader)

        return shader

    def _ValidateUsdShader(self, shader, expectedInputTuples, expectedOutputs):
        for expectedInputTuple in expectedInputTuples:
            (inputName, expectedValue) = expectedInputTuple

            shaderInput = shader.GetInput(inputName)
            self.assertTrue(shaderInput)

            if expectedValue is None:
                self.assertFalse(shaderInput.GetAttr().HasAuthoredValueOpinion())
                continue

            # Validate the input value
            value = shaderInput.Get()
            if (isinstance(value, float) or isinstance(value, Gf.Vec3f)):
                self.assertTrue(Gf.IsClose(value, expectedValue, 1e-6))
            else:
                self.assertEqual(value, expectedValue)

        outputs = {output.GetBaseName() : output.GetTypeName()
            for output in shader.GetOutputs()}

        self.assertEqual(outputs, expectedOutputs)

    def _ValidateUsdShaderOuputs(self, shader, expectedOutputs):

        # Validate shader only has one output
        self.assertEqual(len(shader.GetOutputs()), 1)

        # Validate output's value
        shaderOuput = shader.GetOutputs()[0]
        self.assertEqual(shaderOuput.GetBaseName(), expectedOutputs)

    def testExportStandaloneUsdPreviewSurface(self):
        """
        Tests that a usdPreviewSurface with attribute values but no
        connections authored exports correctly.
        """
        maya_file = os.path.join(self.input_dir, "UsdExportUsdPreviewSurfaceTest", "UsdExportUsdPreviewSurfaceTest.ma")
        cmds.file(maya_file, force=True, open=True)

        usd_file_path = os.path.join(self.temp_dir, "UsdPreviewSurfaceExportTest.usda")
        cmds.mayaUSDExport(mergeTransformAndShape=True, file=usd_file_path,
                           shadingMode='useRegistry')

        stage = Usd.Stage.Open(usd_file_path)

        standaloneMaterial = self._GetUsdMaterial(stage,
            'usdPreviewSurface_StandaloneSG')

        surfaceOutput = standaloneMaterial.GetOutput(UsdShade.Tokens.surface)
        previewSurfaceShader = self._GetSourceShader(surfaceOutput)

        expectedShaderPrimPath = standaloneMaterial.GetPath().AppendChild(
            'usdPreviewSurface_Standalone')

        self.assertEqual(previewSurfaceShader.GetPath(),
            expectedShaderPrimPath)

        self.assertEqual(previewSurfaceShader.GetShaderId(),
            'UsdPreviewSurface')

        expectedInputTuples = [
            ('clearcoat', 0.1),
            ('clearcoatRoughness', 0.2),
            ('diffuseColor', Gf.Vec3f(0.3, 0.4, 0.5)),
            ('displacement', 0.6),
            ('emissiveColor', Gf.Vec3f(0.07, 0.08, 0.09)),
            ('ior', 1.1),
            ('metallic', 0.11),
            ('normal', Gf.Vec3f(0.12, 0.13, 0.14)),
            ('occlusion', 0.9),
            ('opacity', 0.8),
            ('roughness', 0.7),
            ('specularColor', Gf.Vec3f(0.3, 0.2, 0.1)),
            ('useSpecularWorkflow', 1)
        ]

        expectedOutputs = {
            'surface': Sdf.ValueTypeNames.Token,
            'displacement': Sdf.ValueTypeNames.Token
        }

        self._ValidateUsdShader(previewSurfaceShader, expectedInputTuples,
            expectedOutputs)

        # There should not be any additional inputs.
        self.assertEqual(
            len(previewSurfaceShader.GetInputs()), len(expectedInputTuples))

    def testExportConnectedUsdPreviewSurface(self):
        """
        Tests that a UsdPreviewSurface with bindings to other shading nodes
        exports correctly.
        """
        maya_file = os.path.join(self.input_dir, "UsdExportUsdPreviewSurfaceTest", "UsdExportUsdPreviewSurfaceTest.ma")
        cmds.file(maya_file, force=True, open=True)

        usd_file_path = os.path.join(self.temp_dir, "UsdPreviewSurfaceExportTest.usda")
        cmds.mayaUSDExport(mergeTransformAndShape=True, file=usd_file_path,
                           shadingMode='useRegistry')

        stage = Usd.Stage.Open(usd_file_path)

        connectedMaterial = self._GetUsdMaterial(stage,
            'usdPreviewSurface_ConnectedSG')

        surfaceOutput = connectedMaterial.GetOutput(UsdShade.Tokens.surface)
        previewSurfaceShader = self._GetSourceShader(surfaceOutput)

        expectedShaderPrimPath = connectedMaterial.GetPath().AppendChild(
            'usdPreviewSurface_Connected')

        self.assertEqual(previewSurfaceShader.GetPath(),
            expectedShaderPrimPath)

        self.assertEqual(previewSurfaceShader.GetShaderId(),
            'UsdPreviewSurface')

        expectedInputTuples = [
            ('clearcoat', 0.1),
            ('specularColor', Gf.Vec3f(0.2, 0.2, 0.2)),
            ('useSpecularWorkflow', 1)
        ]

        expectedOutputs = {
            'surface': Sdf.ValueTypeNames.Token,
            'displacement': Sdf.ValueTypeNames.Token
        }

        self._ValidateUsdShader(previewSurfaceShader, expectedInputTuples,
            expectedOutputs)

        # There should be four more connected inputs in addition to the inputs
        # with authored values.
        self.assertEqual(len(previewSurfaceShader.GetInputs()),
            len(expectedInputTuples) + 4)

        # Validate the UsdUvTexture prim connected to the UsdPreviewSurface's
        # diffuseColor input.
        diffuseColorInput = previewSurfaceShader.GetInput('diffuseColor')
        difTexShader = self._GetSourceShader(diffuseColorInput)
        self._ValidateUsdShaderOuputs(difTexShader, 'rgb')

        expectedShaderPrimPath = connectedMaterial.GetPath().AppendChild(
            'Brazilian_Rosewood_Texture')

        self.assertEqual(difTexShader.GetPath(), expectedShaderPrimPath)
        self.assertEqual(difTexShader.GetShaderId(), 'UsdUVTexture')

        # Validate the UsdUvTexture prim connected to the UsdPreviewSurface's
        # clearcoatRoughness and roughness inputs. They should both be fed by
        # the same shader prim.
        clearcoatRougnessInput = previewSurfaceShader.GetInput('clearcoatRoughness')
        bmpTexShader = self._GetSourceShader(clearcoatRougnessInput)
        rougnessInput = previewSurfaceShader.GetInput('roughness')
        roughnessShader = self._GetSourceShader(rougnessInput)

        self._ValidateUsdShaderOuputs(bmpTexShader, 'r')
        self._ValidateUsdShaderOuputs(roughnessShader, 'r')

        self.assertEqual(bmpTexShader.GetPrim(), roughnessShader.GetPrim())

        expectedShaderPrimPath = connectedMaterial.GetPath().AppendChild(
            'Brazilian_Rosewood_Bump_Texture')

        self.assertEqual(bmpTexShader.GetPath(), expectedShaderPrimPath)
        self.assertEqual(bmpTexShader.GetShaderId(), 'UsdUVTexture')

        # Validate the UsdUvTexture prim connected to the UsdPreviewSurface's
        # normal input.
        normalColorInput = previewSurfaceShader.GetInput('normal')
        normalTexShader = self._GetSourceShader(normalColorInput)

        self._ValidateUsdShaderOuputs(normalTexShader, 'rgb')

        expectedShaderPrimPath = connectedMaterial.GetPath().AppendChild(
            'Brazilian_Rosewood_Normal_Texture')

        self.assertEqual(normalTexShader.GetPath(), expectedShaderPrimPath)
        self.assertEqual(normalTexShader.GetShaderId(), 'UsdUVTexture')


if __name__ == '__main__':
    unittest.main(verbosity=2)
