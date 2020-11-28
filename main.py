import pymem
import time
import keyboard

# offsets dumped by hazedumper https://github.com/frk1/hazedumper/blob/master/csgo.hpp
crosshair_id = 0xB3E4
spotted = 0x93D
team_num = 0xF4
life_state = 0x25F
health = 0x100
local_player = 0xD3ED14
entity_list = 0x4D533AC
force_attack = 0x3184930


def main():
    # open handle to csgo
    pm = pymem.Pymem('csgo.exe')

    # get base address of client.dll
    client_base = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
    print('Client Base: %s' % client_base)

    # get base address of engine.dll
    engine_base = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll
    print('Engine Base: %s' % engine_base)

    # get local player
    local = pm.read_uint(client_base + local_player)
    print('Local Player: %s' % local)

    while True:
        # get our local team now so we dont have to read it many times
        local_team = pm.read_int(local + team_num)
        crosshair = pm.read_uint(local + crosshair_id)

        # if local player is valid
        # get the entity in our crosshair and shoot if they are valid
        if local:
            entity_crosshair_id = pm.read_uint(client_base + entity_list + (crosshair - 1) * 0x10)
            entity_team = pm.read_int(entity_crosshair_id + team_num)
            entity_health = pm.read_int(entity_crosshair_id + health)
            if crosshair <= 64 and crosshair_id >= 0:
                if entity_team != local_team:
                    if entity_health > 0:
                        if keyboard.is_pressed("z"):
                            pm.write_int(client_base + force_attack, 6)

        # player entities are in the this range
        # loop for the entities so we can get the pointer
        for i in range(1, 32):
            entity = pm.read_int(client_base + entity_list + (i * 0x10))
            if entity:
                entity_team = pm.read_int(entity + team_num)
                if entity_team != local_team:
                    if pm.read_int(entity + health) > 0:
                        pm.write_int(entity + spotted, 28)
        time.sleep(0.01)


if __name__ == '__main__':
    main()
