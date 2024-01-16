
# from pywinauto.application import Application
# from ctypes import wintypes as w, windll, create_unicode_buffer
# import ctypes
import uiautomation as auto
auto.uiautomation.SetGlobalSearchTimeout(1)


class BrowserWindow:
    def __init__(self, browser_name, window_index=1):
        """
        A Browser Window support UIAutomation.

        :param browser_name: Browser name, support 'Google Chrome', 'Firefox', 'Edge', 'Opera', etc.
        :param window_index: Count from back to front, default value 1 represents the most recently created window.
        """
        with auto.UIAutomationInitializerInThread(debug=True):
            print("++++++++++++", browser_name)

            if browser_name == 'Firefox':
                win = auto.Control(
                    Depth=1, ClassName='MozillaWindowClass', foundIndex=window_index)
                if not win.Exists(0.5, 0.2):
                    self.addr_bar = None
                    return
                addr_bar = win.ToolBarControl(Name='Navigation').ComboBoxControl(Depth=1, foundIndex=1) \
                    .EditControl(Depth=1, foundIndex=1)
            else:
                if browser_name == 'Microsoft Edge':
                    win = auto.Control(
                        Depth=1, ClassName='Chrome_WidgetWin_1', SubName='Edge', foundIndex=window_index)
                    if not win.Exists(0.5, 0.2):
                        self.addr_bar = None
                        return
                    addr_bar = win.PaneControl(Depth=1, ClassName="BrowserRootView").PaneControl(Depth=1, ClassName="NonClientView").PaneControl(Depth=1, ClassName="GlassBrowserFrameView").PaneControl(
                        Depth=1, ClassName="BrowserView").PaneControl(Depth=1, ClassName="TopContainerView").ToolBarControl(Depth=1, foundIndex=1).GroupControl(Depth=1, foundIndex=1).EditControl(Depth=1, foundIndex=1)
                elif browser_name == 'Opera':
                    win = auto.Control(Depth=1, ClassName='Chrome_WidgetWin_1',
                                    SubName=browser_name, foundIndex=window_index)
                    if not win.Exists(0.5, 0.2):
                        self.addr_bar = None
                        return
                    addr_bar = win.PaneControl(Depth=1, foundIndex=2).PaneControl(Depth=1, foundIndex=1).Control(Depth=1, foundIndex=2).PaneControl(Depth=1, foundIndex=1).PaneControl(Depth=1, foundIndex=1).Control(
                        Depth=1, foundIndex=1).Control(Depth=1, foundIndex=1).ToolBarControl(Depth=1, foundIndex=1).EditControl(Depth=1, foundIndex=1).Control(Depth=1, foundIndex=2).EditControl(Depth=1, foundIndex=1)
                elif browser_name == 'Google Chrome':
                    win = auto.Control(Depth=1, ClassName='Chrome_WidgetWin_1',SubName=browser_name, foundIndex=window_index)
                    if not win.Exists(1, 0.2):
                        self.addr_bar = None
                        return
                    addr_pane = win.PaneControl(Depth=1, foundIndex=2).PaneControl(
                        Depth=1, foundIndex=1).PaneControl(Depth=1, foundIndex=2).PaneControl(Depth=1, foundIndex=1)
                    # print(addr_pane)
                    addr_bar = addr_pane.ToolBarControl(
                        Depth=1, foundIndex=1).EditControl(Depth=2)
                # TODO:more browser support
                else:
                    self.addr_bar = None
                    return
            if not addr_bar.Exists(1, 0.2):
                self.addr_bar = None
                return
            self.addr_bar = addr_bar

    @property
    def current_tab_url(self):
        """Get current tab url."""
        if self.addr_bar:
            try:
                a = self.addr_bar.GetValuePattern().Value
                return a
            except:
                return None
        return None

# sleep(3)
# start = datetime.datetime.now()
# browser = BrowserWindow('Opera')

# print(browser.current_tab_url)
# end = datetime.datetime.now()
# print(end-start)
