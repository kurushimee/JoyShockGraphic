extends ItemList

const SEARCH_DIR := "\\GyroConfigs"

var configs := []


func _on_jsm_path_set() -> void:
	search_configs(%Settings.jsm_path + SEARCH_DIR)
	init_list()


func search_configs(path):
	print("Searching for configs in: " + path)
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
		printerr("The config path doesn't exist: " + path)


func init_list():
	for config in configs:
		add_item(config.get_basename())
