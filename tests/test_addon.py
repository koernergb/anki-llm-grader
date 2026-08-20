import importlib.util
import pathlib
import sys
import types
import unittest


ADDON_DIR = (
    pathlib.Path(__file__).parents[1] / "add_on" / "anki_llm_grader"
)


class HookList(list):
    pass


class AddonManager:
    def addonFromModule(self, name):
        return "anki_llm_grader"

    def setWebExports(self, name, pattern):
        self.exports = (name, pattern)

    def getConfig(self, name):
        return {}


class Reviewer:
    pass


class WebContent:
    def __init__(self):
        self.css = []
        self.js = []


class AddonIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        hooks = types.SimpleNamespace(
            webview_will_set_content=HookList(),
            webview_did_receive_js_message=HookList(),
            reviewer_did_show_answer=HookList(),
            reviewer_did_show_question=HookList(),
        )
        mw = types.SimpleNamespace(addonManager=AddonManager())

        aqt = types.ModuleType("aqt")
        aqt.gui_hooks = hooks
        aqt.mw = mw
        reviewer_module = types.ModuleType("aqt.reviewer")
        reviewer_module.Reviewer = Reviewer
        webview_module = types.ModuleType("aqt.webview")
        webview_module.WebContent = WebContent

        cls.previous_modules = {
            name: sys.modules.get(name)
            for name in ("aqt", "aqt.reviewer", "aqt.webview", "anki_llm_grader")
        }
        sys.modules.update(
            {
                "aqt": aqt,
                "aqt.reviewer": reviewer_module,
                "aqt.webview": webview_module,
            }
        )

        spec = importlib.util.spec_from_file_location(
            "anki_llm_grader",
            ADDON_DIR / "__init__.py",
            submodule_search_locations=[str(ADDON_DIR)],
        )
        cls.addon = importlib.util.module_from_spec(spec)
        sys.modules["anki_llm_grader"] = cls.addon
        assert spec.loader is not None
        spec.loader.exec_module(cls.addon)
        cls.hooks = hooks

    @classmethod
    def tearDownClass(cls):
        for name, module in cls.previous_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
        sys.modules.pop("anki_llm_grader.grader", None)

    def test_all_hooks_are_registered(self):
        self.assertEqual(len(self.hooks.webview_will_set_content), 1)
        self.assertEqual(len(self.hooks.webview_did_receive_js_message), 1)
        self.assertEqual(len(self.hooks.reviewer_did_show_answer), 1)
        self.assertEqual(len(self.hooks.reviewer_did_show_question), 1)

    def test_reviewer_assets_are_injected_only_for_reviewer(self):
        content = WebContent()
        self.addon._add_reviewer_assets(content, Reviewer())
        self.assertEqual(
            content.css,
            ["/_addons/anki_llm_grader/web/grader.css"],
        )
        self.assertEqual(
            content.js,
            ["/_addons/anki_llm_grader/web/grader.js"],
        )

        other = WebContent()
        self.addon._add_reviewer_assets(other, object())
        self.assertEqual(other.css, [])
        self.assertEqual(other.js, [])


if __name__ == "__main__":
    unittest.main()
