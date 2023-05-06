import os
import sys
import json
import uuid
from cela_algoritms_karte import get_path_map

parameters = sys.argv[1:]
start_cab = int(parameters[0]) if parameters[0].isdigit() else parameters[0]
end_cab = int(parameters[1]) if parameters[1].isdigit() else parameters[1]
start_floor = int(parameters[2]) if parameters[2].isdigit() else parameters[2]
end_floor = int(parameters[3]) if parameters[3].isdigit() else parameters[3]
use_elevator = parameters[4] == '1'
language = parameters[5]
start_floor_map_file_path = str(uuid.uuid4()) + ".png"
end_floor_map_file_path = str(uuid.uuid4())  + ".png"

instructions, output_1, output_2, start_floor, end_floor = get_path_map(
    start_cab=start_cab, end_cab=end_cab,
    start_floor=start_floor, end_floor=end_floor,
    use_elevator=use_elevator,
    language=language,
    destination_file_1=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "path_pics", start_floor_map_file_path),
    destination_file_2=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "path_pics", end_floor_map_file_path))

#instructions, output_1, output_2 = get_path_map(start_cab=123, end_cab=609, use_elevator=False,
#    language='LV',
#    destination_file_1=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "path_pics", "123_lifts.png"),
#    destination_file_2=os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "path_pics", "lifts_wc.png"))

print(json.dumps({ 
    "instructions": instructions, 
    "start_floor_plan": os.path.basename(output_1), 
    "end_floor_plan": os.path.basename(output_2),
    "start_floor": start_floor,
    "end_floor": end_floor,
    }))