extends ItemList

const SEARCH_DIR := "/AutoLoad"
var jsm_path: String

var configs := []


func _ready() -> void:
	jsm_path = OS.get_executable_path().get_base_dir()
	search_configs(jsm_path + SEARCH_DIR)
	init_list()


func search_configs(path):
	var dir := DirAccess.open(path)
	if dir:
		dir.list_dir_begin()

		var file_name := dir.get_next()
		while file_name != "":
			if not dir.current_is_dir():
				var config := file_name
				print("Found config: " + config)
				configs.append(config)

			file_name = dir.get_next()
	else:
		print("An error occurred when trying to access the path.")


func init_list():
	for config in configs:
		print(config.get_basename())
