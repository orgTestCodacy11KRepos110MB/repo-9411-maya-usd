#
# Copyright 2022 Autodesk
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

import maya.cmds as cmds
import maya.mel as mel

from mayaUsdLibRegisterStrings import getMayaUsdLibString
import mayaUsdOptions

from functools import partial


_mergeTarget = None


def showMergeToUSDOptions(target):
    """
    Shows the Merge to USD options dialog.
    """
    _setMergeToUSDTarget(target)

    windowName = "MergeToUSDOptionsDialog"
    if cmds.window(windowName, query=True, exists=True):
        if cmds.window(windowName, query=True, visible=True):
            return
        # If it exists but is not visible, assume something wrong happened.
        # Delete the window and recreate it.
        cmds.deleteUI(windowName)

    window = cmds.window(windowName, title=getMayaUsdLibString("kMergeToUSDOptionsTitle"))
    _createMergeToUSDOptionsDialog(window, target)


def _getMergeToUSDTarget():
    """
    Retrieves the current target for the merge-to-USD command.
    """
    global _mergeTarget
    return _mergeTarget


def _setMergeToUSDTarget(target):
    """
    Sets the current target for the merge-to-USD command.
    """
    global _mergeTarget
    _mergeTarget = target


def _createMergeToUSDOptionsDialog(window, target):
    """
    Creates the merge-to-USD dialog.
    """

    windowLayout = cmds.setParent(query=True)

    menuLayout = cmds.columnLayout("MergeToUSDOptionsDialogMenuLayout", adjustableColumn=True, parent=windowLayout)

    menuBarLayout = cmds.menuBarLayout()

    subLayout = cmds.columnLayout("MergeToUSDOptionsDialogSubLayout", adjustableColumn=True, parent=windowLayout)

    optionsText = getMergeToUSDOptionsText()
    _fillMergeToUSDOptionsDialog(target, subLayout, optionsText, "post")

    menu = cmds.menu(label=getMayaUsdLibString("kEditMenu"), parent=menuBarLayout)
    cmds.menuItem(label=getMayaUsdLibString("kSaveSettingsMenuItem"), command=_saveMergeToUSDOptions)
    cmds.menuItem(label=getMayaUsdLibString("kResetSettingsMenuItem"), command=partial(_resetMergeToUSDOptions, target, subLayout))

    cmds.setParent(menuBarLayout)
    menu = cmds.menu(label=getMayaUsdLibString("kHelpMenu"), parent=menuBarLayout)
    cmds.menuItem(label=getMayaUsdLibString("kHelpMergeToUSDOptionsMenuItem"), command=_helpMergeToUSDOptions)

    buttonsLayout = cmds.formLayout(parent=windowLayout)

    mergeText  = getMayaUsdLibString("kMergeButton")
    applyText  = getMayaUsdLibString("kApplyButton")
    cancelText = getMayaUsdLibString("kCancelButton")
    bMerge     = cmds.button(label=mergeText,  width=100, command=partial(_acceptMergeToUSDOptionsDialog, window))
    bApply     = cmds.button(label=applyText,  width=100, command=_applyMergeToUSDOptionsDialog)
    bCancel    = cmds.button(label=cancelText, width=100, command=partial(_cancelMergeToUSDOptionsDialog, window))

    spacer = 10
    edge   = 20

    cmds.formLayout(buttonsLayout, edit=True,
        attachForm=[
            (bCancel,   "top",    edge),
            (bCancel,   "bottom", edge),
            (bCancel,   "right",  edge),

            (bApply,    "top",    edge),
            (bApply,    "bottom", edge),

            (bMerge,    "top",    edge),
            (bMerge,    "bottom", edge),
            (bMerge,    "left",   edge),
        ],
        attachPosition=[
            (bCancel,   "left",   spacer/2, 67),
            (bApply,    "right",  spacer/2, 67),
            (bApply,    "left",   spacer/2, 33),
            (bMerge,    "right",  spacer/2, 33),
        ])

    cmds.scriptJob(parent=window, event=("SelectionChanged", partial(_updateMergeToUSDOptionsDialogOnSelectionChanged, [bMerge, bApply])))

    cmds.showWindow()


def _updateMergeToUSDOptionsDialogOnSelectionChanged(buttons):
    """
    Reacts to selection changes to enable or disable the merge and apply buttons.
    """
    # If we still are using the original target, don't update the buttons.
    target = _getMergeToUSDTarget()
    if target:
        hasSelection = True
    else:
        hasSelection = len(cmds.ls(sl=True)) > 0
    for button in buttons:
        cmds.button(button, edit=True, enable=hasSelection)


def _acceptMergeToUSDOptionsDialog(window, data=None):
    """
    Reacts to the merge-to-USD options dialog being OK'ed by the user.
    """
    _applyMergeToUSDOptionsDialog(data)
    cmds.deleteUI(window)


def _applyMergeToUSDOptionsDialog(data=None):
    """
    Reacts to the merge-to-USD options dialog being applied by the user.
    """
    _saveMergeToUSDOptions()

    target = _getMergeToUSDTarget()
    if not target:
        sel = cmds.ls(sl=True)
        if len(sel):
            target = sel[0]

    if target:
        optionsText = getMergeToUSDOptionsText()
        cmds.mayaUsdMergeToUsd(target, exportOptions=optionsText)
        # This will force using the current selection if applied again.
        _setMergeToUSDTarget(None)


def _cancelMergeToUSDOptionsDialog(window, data=None):
    """
    Reacts to the merge-to-USD options dialog being canceled by the user.
    """
    cmds.deleteUI(window)


def _saveMergeToUSDOptions(data=None):
    """
    Saves the merge-to-USD options as currently set in the dialog.
    The MEL receiveMergeToUSDOptionsTextFromDialog will call setMergeToUSDOptionsText.
    """
    mel.eval('''mayaUsdTranslatorExport("", "query=all;!output", "", "receiveMergeToUSDOptionsTextFromDialog");''')


def _resetMergeToUSDOptions(target, subLayout, data=None):
    """
    Resets the merge-to-USD options in the dialog.
    """
    optionsText = mayaUsdOptions.convertOptionsDictToText(_getDefaultMergeToUSDOptionsDict())
    _fillMergeToUSDOptionsDialog(target, subLayout, optionsText, "fill")


def _fillMergeToUSDOptionsDialog(target, subLayout, optionsText, action):
    """
    Fills the merge-to-USD options dialog UI elements with the given options.
    """
    cmds.setParent(subLayout)
    optionsText = mayaUsdOptions.setAnimateOption(target, optionsText)
    mel.eval(
        '''
        mayaUsdTranslatorExport("{subLayout}", "{action}=all;!output", "{optionsText}", "")
        '''.format(optionsText=optionsText, subLayout=subLayout, action=action))


def _helpMergeToUSDOptions(data=None):
    """
    Shows help on the merge-to-USD options dialog.
    """
    # TODO: add help about the options UI instead of the merge command
    cmds.help('mayaUsdMergeToUsd', doc=True)


def _getMergeToUSDOptionsVarName():
    """
    Retrieves the option var name under which the merge-to-USD options are kept.
    """
    return "mayaUsd_MergeToUSDOptions"


def getMergeToUSDOptionsText():
    """
    Retrieves the current merge-to-USD options as text with column-spearated key/value pairs.
    """
    return mayaUsdOptions.getOptionsText(
        _getMergeToUSDOptionsVarName(),
        _getDefaultMergeToUSDOptionsDict())
    

def setMergeToUSDOptionsText(optionsText):
    """
    Sets the current merge-to-USD options as text with column-spearated key/value pairs.
    Called via receiveMergeToUSDOptionsTextFromDialog in MEL, which gets called via
    mayaUsdTranslatorExport in query mode.
    """
    mayaUsdOptions.setOptionsText(_getMergeToUSDOptionsVarName(), optionsText)


def _getDefaultMergeToUSDOptionsDict():
    """
    Retrieves the current merge-to-USD options.
    """
    return {
        "exportColorSets":          "1",
        "exportUVs":                "1",
        "exportSkels":              "none",
        "exportSkin":               "none",
        "exportBlendShapes":        "0",
        "exportDisplayColor":       "1",
        "shadingMode":              "none",
        "animation":                "1",
        "exportVisibility":         "1",
        "exportInstances":          "1",
        "mergeTransformAndShape":   "1",
        "stripNamespaces":          "0",
    }
