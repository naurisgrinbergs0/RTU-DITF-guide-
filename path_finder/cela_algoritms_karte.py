from typing import List
import numpy as np
import cv2
from utils.UtilDatabaseCursor import UtilDatabaseCursor
import os
import sys

WALL_MARKER = -8
PATH_MARKER = -1
START_MARKER = 0
FINISH_MARKER = 99
STRAIGHT_INSTR_LV = 'Dodies taisni!'
LEFT_INSTR_LV = 'Nogriezies pa kreisi!'
RIGHT_INSTR_LV = 'Nogriezies pa labi!'
FINISH_INSTR_LV = 'Esi sasniedzis galamērķi!'
STRAIGHT_INSTR_EN = 'Go straight!'
LEFT_INSTR_EN = 'Turn left!'
RIGHT_INSTR_EN = 'Turn right!'
FINISH_INSTR_EN = 'You have reached the destination!'
# WALKING_UNIT = ' blokus'


class FloorMap:
    def __init__(self, floor_map: np.array, floor_nr: int, img_path: str = None, elevator_coord: List[List[int]] = None,
                 stairs_coord: List[List[int]] = None):
        self.floor_map = floor_map
        self.floor_nr = floor_nr
        self.width = floor_map.shape[1]
        self.length = floor_map.shape[0]
        self.marked_map = np.zeros((self.length, self.width))
        self.img_path = img_path
        if not img_path:
            print("Warning! No image path for map assigned")
        self.elevator = elevator_coord
        self.stairs = stairs_coord

    # Izdrukā stāva plānu kāds tas ir ievadīts
    def print_floor_plan(self):
        print(f"\n{self.floor_nr}. stāva floor_map: \n")
        for i in self.floor_map[:][:]:
            print(str(i).replace(' [', '').replace('[', '').replace(']', ''))

    # Izdrukā stāva plānu, ar ceļa garumiem
    def print_marked_map(self):
        line_str = ''

        for y in range(self.length):
            for x in range(self.width):
                if self.marked_map[y][x] == WALL_MARKER:
                    line_str += '_' + '\t'
                else:
                    line_str += str(int(self.marked_map[y][x])) + '\t'
            print(line_str)
            line_str = ''

    # Atrod ceļu no starta pozīcijas, līdz beigu pozīcijai
    def find_path(self, start_pos=None, end_pos=None, end_img_path=None, draw_path_pic=False, language='LV'):

        if start_pos is None or end_pos is None:
            print("ERROR! No start or end position assigned!")
            return -1

        self.mark_map(start_pos, end_pos)
        # Marks the map with how many steps it takes to get to the finish (find the shortest path)
        pos_list = [[start_pos[0], start_pos[1], 0]]  # List of positions on path [y, x, step]
        end_pos_achieved = False
        while not end_pos_achieved:
            for cur_pos in pos_list:
                if cur_pos[0] + 1 < self.length and (self.marked_map[cur_pos[0] + 1][cur_pos[1]] == PATH_MARKER
                                                     or self.marked_map[cur_pos[0] + 1][cur_pos[1]] == FINISH_MARKER):
                    if self.marked_map[cur_pos[0] + 1][cur_pos[1]] == FINISH_MARKER:
                        end_pos_achieved = True
                    else:
                        self.marked_map[cur_pos[0] + 1][cur_pos[1]] = cur_pos[-1] + 1
                        pos_list.append([cur_pos[0] + 1, cur_pos[1], cur_pos[-1] + 1])

                if cur_pos[1] + 1 < self.width and (self.marked_map[cur_pos[0]][cur_pos[1] + 1] == PATH_MARKER
                                                    or self.marked_map[cur_pos[0]][cur_pos[1] + 1] == FINISH_MARKER):
                    if self.marked_map[cur_pos[0]][cur_pos[1] + 1] == FINISH_MARKER:
                        end_pos_achieved = True
                    else:
                        self.marked_map[cur_pos[0]][cur_pos[1] + 1] = cur_pos[-1] + 1
                        pos_list.append([cur_pos[0], cur_pos[1] + 1, cur_pos[-1] + 1])

                if cur_pos[0] - 1 >= 0 and (self.marked_map[cur_pos[0] - 1][cur_pos[1]] == PATH_MARKER
                                            or self.marked_map[cur_pos[0] - 1][cur_pos[1]] == FINISH_MARKER):
                    if self.marked_map[cur_pos[0] - 1][cur_pos[1]] == FINISH_MARKER:
                        end_pos_achieved = True
                    else:
                        self.marked_map[cur_pos[0] - 1][cur_pos[1]] = cur_pos[-1] + 1
                        pos_list.append([cur_pos[0] - 1, cur_pos[1], cur_pos[-1] + 1])

                if cur_pos[1] - 1 >= 0 and (self.marked_map[cur_pos[0]][cur_pos[1] - 1] == PATH_MARKER
                                            or self.marked_map[cur_pos[0]][cur_pos[1] - 1] == FINISH_MARKER):
                    if self.marked_map[cur_pos[0]][cur_pos[1] - 1] == FINISH_MARKER:
                        end_pos_achieved = True
                    else:
                        self.marked_map[cur_pos[0]][cur_pos[1] - 1] = cur_pos[-1] + 1
                        pos_list.append([cur_pos[0], cur_pos[1] - 1, cur_pos[-1] + 1])

        # self.print_marked_map()

        # 'step': [positions] , there can be multiple position values in one step value
        pos_steps = {}
        for i in pos_list:
            # print(i)
            if i[-1] not in pos_steps.keys():
                pos_steps[i[-1]] = [i[:-1]]
            else:
                pos_steps[i[-1]].append(i[:-1])

        # get the number of steps that is the closest to the end (how many steps(max) are needed)
        steps = 0
        for i in pos_steps.keys():
            if [end_pos[0] + 1, end_pos[1]] in pos_steps.get(i) or [end_pos[0] - 1, end_pos[1]] in pos_steps.get(i) \
                    or [end_pos[0], end_pos[1] + 1] in pos_steps.get(i) or [end_pos[0],
                                                                            end_pos[1] - 1] in pos_steps.get(i):
                steps = i
                break

        # shortest path {'step': position}
        path = {}
        for i in range(steps, -1, -1):
            if len(pos_steps.get(i)) == 1:
                path[i] = pos_steps.get(i)[0]
            else:
                if len(path) == 0:
                    prev_pos = end_pos
                else:
                    prev_pos = path.get(i + 1)
                if [prev_pos[0] + 1, prev_pos[1]] in pos_steps.get(i):
                    path[i] = [prev_pos[0] + 1, prev_pos[1]]
                elif [prev_pos[0] - 1, prev_pos[1]] in pos_steps.get(i):
                    path[i] = [prev_pos[0] - 1, prev_pos[1]]
                elif [prev_pos[0], prev_pos[1] + 1] in pos_steps.get(i):
                    path[i] = [prev_pos[0], prev_pos[1] + 1]
                elif [prev_pos[0], prev_pos[1] - 1] in pos_steps.get(i):
                    path[i] = [prev_pos[0], prev_pos[1] - 1]
        path[steps + 1] = end_pos
        # a w s d, {'step': move}
        moves = {}
        # print("Ceļš: ")
        # print(path)
        for i in range((steps + 2)):
            # print(path.get(i))
            if path.get(i + 1) is not None:
                this_pos = path.get(i)
                next_pos = path.get(i + 1)
                if this_pos[0] + 1 == next_pos[0]:
                    moves[i] = 's'
                elif this_pos[0] - 1 == next_pos[0]:
                    moves[i] = 'w'
                elif this_pos[1] + 1 == next_pos[1]:
                    moves[i] = 'd'
                elif this_pos[1] - 1 == next_pos[1]:
                    moves[i] = 'a'

        # print("Gājieni")
        # print(moves)
        if language != 'LV' and language != 'EN':
            language = 'LV'
        if language == 'LV':
            STRAIGHT_INSTR = STRAIGHT_INSTR_LV
            LEFT_INSTR = LEFT_INSTR_LV
            RIGHT_INSTR = RIGHT_INSTR_LV
            FINISH_INSTR = FINISH_INSTR_LV
        else:
            STRAIGHT_INSTR = STRAIGHT_INSTR_EN
            LEFT_INSTR = LEFT_INSTR_EN
            RIGHT_INSTR = RIGHT_INSTR_EN
            FINISH_INSTR = FINISH_INSTR_EN

        instructions_1 = {}
        changing_direction_pos = {0: start_pos}
        dir_pos = 1
        for i in range(len(moves)):
            if moves.get(i + 1) is None:
                instructions_1[i] = FINISH_INSTR
                changing_direction_pos[dir_pos] = end_pos
                # changing_direction_pos[dir_pos+1] = end_pos
            else:
                cm = moves.get(i)
                nm = moves.get(i + 1)
                moves_comb = [cm, nm]
                if moves.get(i + 1) == moves.get(i):
                    instructions_1[i] = STRAIGHT_INSTR
                    # if instructions_1.get(i-1) != 'Ej taisni!':

                if moves_comb == ['w', 'd'] or moves_comb == ['d', 's'] or moves_comb == ['s', 'a'] or moves_comb == [
                    'a', 'w']:
                    instructions_1[i] = RIGHT_INSTR
                    changing_direction_pos[dir_pos] = path.get(i + 1)
                    dir_pos += 1
                if moves_comb == ['w', 'a'] or moves_comb == ['a', 's'] or moves_comb == ['s', 'd'] or moves_comb == [
                    'd', 'w']:
                    instructions_1[i] = LEFT_INSTR
                    changing_direction_pos[dir_pos] = path.get(i + 1)
                    dir_pos += 1

        # print("Pozīcijas maiņas:")
        # print(changing_direction_pos)
        if draw_path_pic:
            self.draw_path(changing_direction_pos, end_img_path)

        instructions = {}
        moves_count = 0
        walking_straight = 0
        for i in range(len(instructions_1)):

            if instructions_1.get(i) != STRAIGHT_INSTR:
                instructions[moves_count] = instructions_1.get(i)
                moves_count += 1
                walking_straight = 0
            else:
                if instructions_1.get(i) == instructions_1.get(i + 1):
                    walking_straight += 1
                    pass
                else:
                    # TODO ar daudzumu?
                    instructions[moves_count] = instructions_1.get(i)  # + f' {walking_straight + 2}' + WALKING_UNIT
                    moves_count += 1
        # instructions ir instrukcijas pēc kārtas, kā jāveic darbības
        # for i in range(len(instructions)):
        #     print(instructions.get(i))
        # print(instructions)
        return instructions, path

    def mark_map(self, start_pos, end_pos):

        for x in range(self.width):
            for y in range(self.length):
                if self.floor_map[y][x] == 0:
                    self.marked_map[y][x] = PATH_MARKER
                else:
                    self.marked_map[y][x] = WALL_MARKER
        self.marked_map[start_pos[0]][start_pos[1]] = START_MARKER
        self.marked_map[end_pos[0]][end_pos[1]] = FINISH_MARKER

    def draw_path(self, change_pos, end_img_path=None):
        # TODO dict ar {'pos': 'pic_loc'}
        path = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), self.img_path)

        image = cv2.imread(path)
        # izmērs = image.shape[:-1]  (y, x)
        pic_size = image.shape[:-1]
        y_ratio = pic_size[0] / self.length
        x_ratio = pic_size[1] / self.width
        color = (255, 0, 255)
        thickness = int(min(x_ratio, y_ratio) / 5)

        for i in range(len(change_pos)):
            if i == 0:
                image = cv2.circle(image, (
                    int((0.5 + change_pos.get(i)[1]) * x_ratio), int((0.5 + change_pos.get(i)[0]) * y_ratio)),
                                   int(min(x_ratio, y_ratio) / 2), (0, 0, 255), -1)

            else:
                start_point = (
                    int((0.5 + change_pos.get(i - 1)[1]) * x_ratio), int((0.5 + change_pos.get(i - 1)[0]) * y_ratio))
                end_point = (int((0.5 + change_pos.get(i)[1]) * x_ratio), int((0.5 + change_pos.get(i)[0]) * y_ratio))
                image = cv2.line(image, start_point, end_point,
                                 color, thickness)
            if i == len(change_pos) - 1:
                image = cv2.circle(image, (
                    int((0.5 + change_pos.get(i)[1]) * x_ratio), int((0.5 + change_pos.get(i)[0]) * y_ratio)),
                                   int(min(x_ratio, y_ratio) / 2), (0, 255, 0), -1)

        # Using cv2.imwrite() method
        # Saving the image
        if end_img_path:
            end_path = end_img_path
        else:
            end_path = f'output_{self.img_path}'
        cv2.imwrite(end_path, image)

    def draw_path_coord(self, change_pos, end_img_path=None):
        # TODO dict ar {'pos': 'pic_loc'}
        # path_to_img = {[16, 12]: (595, 600), [1, 12]: (595, 145), [1, 7]: (355, 145), [2, 7]: (355, 180)}
        # !!! path_to_img = {'x': {15: 600, 1: 145, 2, 180}, 'y':{12: 600, 7: 355} }
        path_to_img = {0: (595, 600), 1: (595, 145), 2: (355, 145), 3: (355, 180)}
        path = self.img_path

        image = cv2.imread(path)
        # izmērs = image.shape[:-1]  (y, x)
        pic_size = image.shape[:-1]
        y_ratio = pic_size[0] / self.length
        x_ratio = pic_size[1] / self.width
        color = (255, 0, 255)
        thickness = int(min(x_ratio, y_ratio) / 10)

        for i in range(len(change_pos)):
            if i == 0:
                point = path_to_img.get(i)
                image = cv2.circle(image, point, int(min(x_ratio, y_ratio) / 2), (0, 0, 255), -1)

            else:
                start_point = path_to_img.get(i - 1)
                end_point = path_to_img.get(i)
                image = cv2.line(image, start_point, end_point,
                                 color, thickness)
            if i == len(change_pos) - 1:
                point = path_to_img.get(i)
                image = cv2.circle(image, point,
                                   int(min(x_ratio, y_ratio) / 2), (0, 255, 0), -1)

        # Using cv2.imwrite() method
        # Saving the image
        if end_img_path:
            end_path = end_img_path
        else:
            end_path = f'output1_{self.img_path}'
        cv2.imwrite(end_path, image)

    # print(cels_karte)


class Building:

    def __init__(self, floors: int = 0):
        self.maps = {}
        self.floors = floors

    def add_floor_plan(self, floor_map: FloorMap):
        if floor_map.floor_nr <= self.floors:
            self.maps[floor_map.floor_nr] = floor_map
        else:
            print("ERROR")

    def find_path(self, start_coord, start_floor, end_coord, end_floor, use_elevator=False, language='LV',
        destination_file_1=None,
        destination_file_2=None):
        if self.maps.get(start_floor) is None or self.maps.get(end_floor) is None:
            print("ERROR this floor does not exist on the map or has not been added yet")
            return -1

        else:
            if language != 'LV' and language != 'EN':
                language = 'LV'
            if language == 'LV':
                FINISH_INSTR = FINISH_INSTR_LV
            else:
                FINISH_INSTR = FINISH_INSTR_EN
            start_floor_map = self.maps.get(start_floor)
            end_floor_map = self.maps.get(end_floor)
            instructions = {}
            if start_floor_map.floor_map[start_coord[0], start_coord[1]] != 0 or \
                    end_floor_map.floor_map[end_coord[0], end_coord[1]] != 0:
                print("ERROR cabinet coordination ar not on the path")
                return -1

            if start_floor == end_floor:
                if not destination_file_1:
                    destination_file_1 = './path_pics/output.png'
                instructions, _ = start_floor_map.find_path(start_pos=start_coord,
                                                            end_pos=end_coord,
                                                            end_img_path=destination_file_1,
                                                            draw_path_pic=True, language=language)
            elif start_floor != end_floor:
                if not destination_file_1:
                    destination_file_1 = './path_pics/output_1.png'
                if not destination_file_2:
                    destination_file_2 = './path_pics/output_2.png'
                closest_el_st = {}
                if use_elevator:
                    for i in start_floor_map.elevator:
                        _, path = start_floor_map.find_path(start_pos=start_coord, end_pos=i)
                        step_count = len(path)
                        closest_el_st[step_count] = i
                else:
                    for i in start_floor_map.stairs:
                        _, path = start_floor_map.find_path(start_pos=start_coord, end_pos=i)
                        step_count = len(path)
                        closest_el_st[step_count] = i
                closest_el_st_pos = closest_el_st.get(min(closest_el_st.keys()))
                closest_el_st_name = get_elevator_stairs_name(closest_el_st_pos, start_floor)

                first_instructions, _ = start_floor_map.find_path(start_pos=start_coord,
                                                                  end_pos=closest_el_st_pos,
                                                                  end_img_path=destination_file_1,
                                                                  draw_path_pic=True, language=language)
                i = 0
                for j in range(len(first_instructions)):
                    if first_instructions.get(i) == FINISH_INSTR:
                        continue
                    else:
                        instructions[i] = first_instructions.get(i)
                        i += 1
                if language == 'LV':
                    instructions[i] = f'Dodies uz {end_floor}. stāvu'
                else:
                    instructions[i] = f'Go to {end_floor}. floor'

                end_start_pos = get_elevator_stairs_position(closest_el_st_name, end_floor)
                end_instructions, _ = end_floor_map.find_path(start_pos=end_start_pos,
                                                              end_pos=end_coord,
                                                              end_img_path=destination_file_2,
                                                              draw_path_pic=True, language=language)
                for j in range(len(end_instructions)):
                    i += 1
                    instructions[i] = end_instructions.get(j)
            else:
                print("ERROR")
                return -1
        return instructions, destination_file_1, destination_file_2


def get_elevator_stairs_name(coordinates, floor):
    with UtilDatabaseCursor() as cursor:
        cursor.execute(
            "SELECT cabinet_nr FROM cabinets_array "
            "WHERE array_place = :coordinates AND floor= :floor;",
            {
                'coordinates': str(coordinates),
                'floor': floor,
            }
        )
        el_st_name_tuple = cursor.fetchone()
        cursor.close()
        if el_st_name_tuple:
            el_st_name = el_st_name_tuple[0]
        else:
            print("DOESN'T EXIST")
            exit()
        return el_st_name


def get_elevator_stairs_position(name, floor):
    with UtilDatabaseCursor() as cursor:
        cursor.execute(
            "SELECT array_place FROM cabinets_array "
            "WHERE cabinet_nr = :cabinet_nr AND floor= :floor;",
            {
                'cabinet_nr': name,
                'floor': floor,
            }
        )
        el_st_place_tuple = cursor.fetchone()
        cursor.close()
        if el_st_place_tuple:
            el_st_place = list(map(int, el_st_place_tuple[0].strip('][').split(', ')))
        else:
            print("DOESN'T EXIST")
            exit()
        return el_st_place


def add_floor_to_db(array_fl, path_to_floor_pic, floor_nr):
    # './floor_plans/floor1.jpg'
    with UtilDatabaseCursor() as cursor:
        cursor.execute(
            "INSERT INTO floor_maps (floor_nr, floor_array, path_to_pic, shape_0, shape_1) "
            "VALUES (:floor_nr, :floor_array, :path_to_pic, :shape_0, :shape_1);",
            {
                'floor_nr': floor_nr,
                'floor_array': array_fl.tostring(),
                'path_to_pic': path_to_floor_pic,
                'shape_0': array_fl.shape[0],
                'shape_1': array_fl.shape[1]
             }
        )
        cursor.close()
    print(f"Floor map for {floor_nr} added")


def edit_floor_db(array_fl, floor_nr):
    # './floor_plans/floor1.jpg'
    with UtilDatabaseCursor() as cursor:

        cursor.execute(
            "UPDATE floor_maps SET (floor_array) "
            "= (:floor_array) WHERE floor_nr = :floor_nr;",
            {
                'floor_array': array_fl.tostring(),
                'floor_nr': floor_nr
             }
        )
        cursor.close()


def add_cabinets_to_db(cabinets_list, cabinets_floor):
    with UtilDatabaseCursor() as cursor:
        for i in cabinets_list:
            cursor.execute(
                "INSERT INTO cabinets_array (cabinet_nr, array_place, floor) "
                "VALUES (:cabinet_nr, :array_place, :floor);",
                {'cabinet_nr': i,
                 'array_place': str(cabinets_list.get(i)),
                 'floor': cabinets_floor,
                 }
            )
        cursor.close()


def get_path_map(
        start_cab=None,
        end_cab=None,
        floors=6,
        start_floor=1,
        end_floor=1,
        use_elevator=False,
        language='LV',
        destination_file_1=None,
        destination_file_2=None
):
    if not start_cab:
        start_cab = 0
    elif type(start_cab) == int:
        start_floor = int(str(start_cab)[0])
    if not end_cab:
        print("NO FINISH DESTINATION!")
        return -1
    DITF_map = Building(floors=floors)

    if type(end_cab) == int:
        end_floor = int(str(end_cab)[0])

    with UtilDatabaseCursor() as cursor:
        cursor.execute(
            "SELECT floor_array, path_to_pic, shape_0, shape_1 FROM floor_maps"
            " WHERE floor_nr = :start_floor; ",
            {'start_floor': start_floor}
        )

        floor_array_start, path_to_pic_start, shape_0_start, shape_1_start = cursor.fetchone()
        floor_DITF_start = np.frombuffer(floor_array_start, int).reshape(shape_0_start, shape_1_start)

        cursor.execute(
            "SELECT  cabinet_nr, array_place FROM cabinets_array"
            " WHERE floor = :start_floor;",
            {'start_floor': start_floor}

        )
        elevator = []
        stairs = []
        for (cabinet_nr, array_place) in cursor.fetchall():
            if 'el' in cabinet_nr:
                elevator.append(list(map(int, array_place.strip('][').split(', '))))
            elif 'k' in cabinet_nr:
                stairs.append(list(map(int, array_place.strip('][').split(', '))))

        DITF_start_floor = FloorMap(floor_DITF_start, start_floor, path_to_pic_start, elevator_coord=elevator,
                                    stairs_coord=stairs)
        DITF_map.add_floor_plan(DITF_start_floor)
        if start_floor != end_floor:
            cursor.execute(
                "SELECT floor_array, path_to_pic, shape_0, shape_1 FROM floor_maps"
                " WHERE floor_nr = :end_floor; ",
                {'end_floor': end_floor}
            )

            floor_array_end, path_to_pic_end, shape_0_end, shape_1_end = cursor.fetchone()
            floor_DITF_end = np.frombuffer(floor_array_end, int).reshape(shape_0_end, shape_1_end)

            cursor.execute(
                "SELECT  cabinet_nr, array_place FROM cabinets_array"
                " WHERE floor = :end_floor;",
                {'end_floor': end_floor}

            )
            elevator_end = []
            stairs_end = []
            for (cabinet_nr, array_place) in cursor.fetchall():
                if 'el' in cabinet_nr:
                    elevator_end.append(list(map(int, array_place.strip('][').split(', '))))
                elif 'k' in cabinet_nr:
                    stairs_end.append(list(map(int, array_place.strip('][').split(', '))))

            DITF_end_floor = FloorMap(floor_DITF_end, end_floor, path_to_pic_end, elevator_coord=elevator_end,
                                      stairs_coord=stairs_end)
            DITF_map.add_floor_plan(DITF_end_floor)

        cursor.execute(
            "SELECT array_place FROM cabinets_array"
            " WHERE cabinet_nr = :start_cab AND floor = :start_floor ;",
            {
                "start_cab": start_cab,
                "start_floor": start_floor
            }
        )
        start_coord_str = cursor.fetchone()
        if start_coord_str:
            start_coord = list(map(int, start_coord_str[0].strip('][').split(', ')))
        else:
            print("Wrong start coord!")
            return -1
            # exit()

        cursor.execute(
            "SELECT array_place FROM cabinets_array"
            " WHERE cabinet_nr = :end_cab AND floor = :end_floor ; ",
            {
                "end_cab": end_cab,
                "end_floor": end_floor
            }
        )
        end_coord_str = cursor.fetchone()
        if end_coord_str:
            end_coord = list(map(int, end_coord_str[0].strip('][').split(', ')))
        else:
            print("Wrong end coord!")
            return -1
            # exit()

        cursor.close()
    full_instructions, output_1, output_2 = DITF_map.find_path(start_coord=start_coord, start_floor=start_floor,
                                                               end_coord=end_coord, end_floor=end_floor,
                                                               use_elevator=use_elevator, language=language,
                                                               destination_file_1=destination_file_1,
                                                               destination_file_2=destination_file_2)
    return full_instructions, output_1, output_2, start_floor, end_floor


if __name__ == '__main__':
    #TODO ievade 1 vai 2 kabineti
    # izvade - instrukcijas un path_to_img?

    instructions, output_1, output_2 = get_path_map(start_cab=206, end_cab='wc', use_elevator=False, language='EN',
                                                    destination_file_1='./path_pics/izmeginajums.png',
                                                    destination_file_2='./path_pics/izmeginajums_2.png')

    for i in instructions:
        print(instructions.get(i))
    print(instructions)
    print(output_1)
    print(output_2)
