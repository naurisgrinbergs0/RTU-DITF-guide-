To get instructions and pictures of path from start to end destination, all you need to do is 
add `from cela_algoritms_karte import get_path_map` to your code and then call function `get_path_map()`

Or just run the `main.py` file.


`get_path_map()` Input:

        start_cab=None,
        end_cab=None,
        floors=6,
        start_floor=1,
        end_floor=1,
        use_elevator=False,
        language='LV',
        destination_file_1=None,
        destination_file_2=None

`start_cab` - starting point(by default the entrance)

`end_cab` - end destination. This **HAS** to be defined. If None, then it will show error and the program will stop

`floors` - number of floors in building. By default, 6. **Should not change or give this argument** unless it is necessary to do so

`start_floor` - the floor of starting point. Not necessary with cabinet numbers as it is generated automatically from the first digit. (Should be used with 'wc')

`end_floor` - same as start_floor

`use_elevator` - If True, use elevator to get between different floors. By default, False aka uses stairs to get from one floor to another.

`language` - By default, 'LV'. Should pass as an argument, if language is 'EN'.

`destination_file_1` - Path to saved image of 1st map. Can be not defined as it will automatically be './path_pics/output.png' or './path_pics/output_1.png'

`destination_file_2` - Path to saved image of 2nd map (If exists. It will only exist if need to change floors). Can be not defined as it will automatically be './path_pics/output_2.png'

### `Only the end_cab is 100% needed. Any others should be defined if required.`


**Output:** instructions, path to 1st image and path to 2nd image(if exists)

Instructions is a dictionary where keys are the order of steps and values are the instructions. For example {1: 'Go straight!', 2: 'Turn left!' }