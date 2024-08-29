import os
import uiautomator2 as u2
import xml.etree.ElementTree as ET

def adb_devices() -> str:  # 取得所有模擬器名稱與狀態
    cmd = 'adb devices'
    process = os.popen(cmd)
    result = process.read().split('\n')
    text = []
    for line in result:
        if 'List of devices' not in line and line != '' and line != ' ':  # 去掉標題跟空白字串
            text.append(line)
    devices = {}
    for i in range(len(text)):
        words = text[i].split('\t')  # 格式: emulator-5554\tdevice
        if 'device' in words[1]:  # 只存有啟動的模擬器
            devices[i] = words[0]  # 用模擬器index當key
    if len(devices) == 0:
        print('[x] None emulator is running')
        raise Exception
    return devices

def connect_single_device(emulator: str) -> u2.Device:
    try:
        d = u2.connect(emulator)
        return d
    except:
        print('[x] Unable to connect to the emulator')
        raise Exception

def generate_xpath(view):
    """
    根據 View 的屬性生成 XPath。
    :param view: View的屬性字典
    :return: 生成的 XPath 字符串
    """
    xpath = f"//{view['class']}"

    conditions = []
    if view['index']:
        conditions.append(f"@index='{view['index']}'")
    if view['text']:
        conditions.append(f"@text='{view['text']}'")
    if view['resource-id']:
        conditions.append(f"@resource-id='{view['resource-id']}'")
    if view['package']:
        conditions.append(f"@package='{view['package']}'")
    if view['content-desc']:
        conditions.append(f"@content-desc='{view['content-desc']}'")
    if view['clickable']:
        conditions.append(f"@clickable='{view['clickable']}'")

    if conditions:
        xpath += "[" + " and ".join(conditions) + "]"

    return xpath

def main(emulator: str):
    d = connect_single_device(emulator)

    # get the UI hierarchy dump content
    xml = d.dump_hierarchy(compressed=False, pretty=True, max_depth=50)
    root = ET.fromstring(xml)

    if clickable_views.get(activity_level) is None:
        clickable_views[activity_level] = []
    if editable_views.get(activity_level) is None:
        editable_views[activity_level] = []

    # Find all clickable & editable views
    for view in root.iter():
        resource_id = view.attrib.get('resource-id', '')
        clickable = view.attrib.get('clickable', 'false')
        package_name = view.attrib.get('package', '')
        if any(app_name.lower() in a for a in [resource_id, package_name]) and clickable == 'true':
            print("Clickable View XPATH: ", generate_xpath(view.attrib))
    for view in root.findall(".//*[@class='android.widget.EditText']"):
        resource_id = view.attrib.get('resource-id', '')
        if app_name.lower() in resource_id:
            print("Editable View XPATH: ", generate_xpath(view.attrib))

if __name__ == '__main__':
    clickable_views = {}
    editable_views = {}
    app_name = 'Spotify'
    activity_level = 0

    try:
        emulators = adb_devices()
    except:
        print('[x] Cannot get the list of emulators, the program will be terminated. Please use adb devices to check if the emulator is running')
        exit()

    main(emulators[0])