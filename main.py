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

# our pointers that we modify when in game
local = 0x0
client_base = 0x0
engine_base = 0x0
local_team = 0x0


def triggerbot():
    crosshair = pm.read_uint(local + crosshair_id)
    # if local player
    if local:
        # get the entity only in our crosshair
        entity_crosshair_id = pm.read_uint(client_base + entity_list + (crosshair - 1) * 0x10)
        # read entity team so we can only hit enemies
        entity_team = pm.read_int(entity_crosshair_id + team_num)
        # read entity health to know if they are alive or not
        entity_health = pm.read_int(entity_crosshair_id + health)
        if crosshair <= 64 and crosshair_id >= 0:
            if entity_team != local_team:
                if entity_health > 0:
                    if keyboard.is_pressed(56):
                        # write to force an attack in game(could be replaced with forcing mouse input)
                        pm.write_int(client_base + force_attack, 6)


def radar():
    # player entities are in the this range
    for i in range(1, 32):
        # read our entity from the entity list
        entity = pm.read_int(client_base + entity_list + (i * 0x10))
        if entity:
            # read the entity team number so we can compare to our global local team pointer
            entity_team = pm.read_int(entity + team_num)
            if entity_team != local_team:
                if pm.read_int(entity + health) > 0:
                    # force b_spotted offset to true since its a bool
                    pm.write_int(entity + spotted, 28)


def main():
    # open handle to csgo
    global pm
    pm = pymem.Pymem('csgo.exe')

    # get base address of client.dll
    global client_base
    client_base = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
    print('Client Base: %s' % client_base)

    # get base address of engine.dll
    global engine_base
    engine_base = pymem.process.module_from_name(pm.process_handle, "engine.dll").lpBaseOfDll
    print('Engine Base: %s' % engine_base)

    # get local player
    global local
    local = local + pm.read_uint(client_base + local_player)
    print('Local Player: %s' % local)

    while True:
        # get our local team now so we don't have to read it many times in different functions
        global local_team
        local_team = pm.read_int(local + team_num)

        # call our functions
        triggerbot()
        radar()

        # sleep so there is some sort of delay for performance increase
        time.sleep(0.01)


if __name__ == '__main__':
    main()
