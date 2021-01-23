import pymem
import time
import keyboard
import sys
import numpy as np
import vectormath as vmath
from requests import get

# automatically get updated offsets from hazedumper
try:
    # Credits to https://github.com/frk1/hazedumper
    haze = get("https://raw.githubusercontent.com/frk1/hazedumper/master/csgo.json").json()
    signatures = haze["signatures"]
    netvars = haze["netvars"]
except:
    sys.exit("Unable to fetch Offsets")


class offsets:
    # signatures
    dormant = signatures["m_bDormant"]
    local_player = signatures["dwLocalPlayer"]
    entity_list = signatures["dwEntityList"]
    force_attack = signatures["dwForceAttack"]
    client_state = signatures["dwClientState"]

    # netvars
    crosshair_id = netvars["m_iCrosshairId"]
    spotted = netvars["m_bSpotted"]
    team_num = netvars["m_iTeamNum"]
    life_state = netvars["m_lifeState"]
    health = netvars["m_iHealth"]
    item_def_index = netvars["m_iItemDefinitionIndex"]
    original_owner_xuid_high = netvars["m_OriginalOwnerXuidHigh"]
    original_owner_xuid_low = netvars["m_OriginalOwnerXuidLow"]
    item_id_high = netvars["m_iItemIDHigh"]
    h_my_weapons = netvars["m_hMyWeapons"]
    fallback_stattrak = netvars["m_nFallbackStatTrak"]
    fallback_paint_kit = netvars["m_nFallbackPaintKit"]
    fallback_seed = netvars["m_nFallbackSeed"]
    fallback_wear = netvars["m_flFallbackWear"]


# our pointers that we modify when in game
local = 0x0
client_base = 0x0
engine_base = 0x0
local_team = 0x0


def triggerbot():
    crosshair = pm.read_uint(local + offsets.crosshair_id)
    # get the entity only in our crosshair
    entity_crosshair_id = pm.read_uint(client_base + offsets.entity_list + (crosshair - 1) * 0x10)
    # if local player
    if local:
        # read entity team so we can only hit enemies
        entity_team = pm.read_uint(entity_crosshair_id + offsets.team_num)
        # read entity health to know if they are alive or not
        entity_health = pm.read_uint(entity_crosshair_id + offsets.health)
        if crosshair <= 64 and offsets.crosshair_id >= 0:
            if entity_team != local_team and entity_health > 0:
                if keyboard.is_pressed(56):
                    # write to force an attack in game(could be replaced with forcing mouse input)
                    pm.write_int(client_base + offsets.force_attack, 6)


def radar():
    # player entities are in the this range
    for i in range(1, 32):
        # read our entity from the entity list
        entity = pm.read_uint(client_base + offsets.entity_list + (i * 0x10))
        if entity:
            # read the entity team number so we can compare to our global local team pointer
            entity_team = pm.read_uint(entity + offsets.team_num)
            # read the entity health so we only show enemies that are alive
            entity_health = pm.read_uint(entity + offsets.health)
            if entity_team != local_team and entity_health > 0:
                # force b_spotted offset to true since its a bool
                pm.write_uint(entity + offsets.spotted, 28)


def main():
    # our handle to csgo process
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
    local = local + pm.read_uint(client_base + offsets.local_player)
    print('Local Player: %s' % local)

    # get our local team now so we don't have to read it many times in different functions
    global local_team
    local_team = pm.read_uint(local + offsets.team_num)
    print('Local Player Team: %s' % local_team)

    while True:
        # call our functions
        triggerbot()
        radar()
        # sleep so there is some sort of delay for performance increase
        time.sleep(0.01)


if __name__ == '__main__':
    main()
