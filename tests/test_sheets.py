from tools.sheets_tool import SheetsTool


def test_completion_detection():
    assert SheetsTool._is_completed({"완료일": "260620"}, ("완료일",))
    assert SheetsTool._is_completed({"상태": "완료"}, ("상태",))
    assert not SheetsTool._is_completed({"상태": "진행중"}, ("상태",))

