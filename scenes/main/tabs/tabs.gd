extends TabContainer

const EDITOR_TAB := 1


func _ready() -> void:
	set_tab_disabled(EDITOR_TAB, true)
