extends Node

signal jsm_path_set


func _ready() -> void:
	if not is_path_set():
		$JsmPathDialog.show()


func _on_path_selected(dir: String) -> void:
	print("JoyShockMapper path set to: " + dir)
	%Settings.jsm_path = dir
	jsm_path_set.emit()


func is_path_set() -> bool:
	if not %Settings.jsm_path:
		return false
	return DirAccess.dir_exists_absolute($Settings.jsm_path)
