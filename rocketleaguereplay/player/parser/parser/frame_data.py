def update_game_data(update, frames, i):
    if 'TAGame.GameEvent_Soccar_TA:SecondsRemaining' in update.keys():
        frames[i]['time']['game_time'] = \
            update['TAGame.GameEvent_Soccar_TA:SecondsRemaining']


def update_car_data(update, frames, i, player_id):
    from player.parser.parser.location import \
        parse_loc_update, parse_rot_update, \
        parse_sleep_update, parse_lin_vel_update, parse_ang_vel_update

    if 'TAGame.RBActor_TA:ReplicatedRBState' in update.keys():
        loc = parse_loc_update(update)
        rot = parse_rot_update(update)
        ang_vel = parse_ang_vel_update(update)
        lin_vel = parse_lin_vel_update(update)
        sleep = parse_sleep_update(update)

        if loc:
            frames[i]['cars'][player_id]['loc'].update(loc)
        if rot:
            frames[i]['cars'][player_id]['rot'].update(rot)
        if ang_vel:
            frames[i]['cars'][player_id]['ang_vel'].update(ang_vel)
        if lin_vel:
            frames[i]['cars'][player_id]['lin_vel'].update(lin_vel)
        if sleep:
            frames[i]['cars'][player_id]['sleep'] = sleep
    if 'TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount' in update.keys():
        frames[i]['cars'][player_id]['boost'] = \
            update['TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount'] / 255
    if 'TAGame.Vehicle_TA:ReplicatedThrottle' in update.keys():
        frames[i]['cars'][player_id]['throttle'] = \
            (update['TAGame.Vehicle_TA:ReplicatedThrottle'] / 255) * 2 - 1
    if 'TAGame.Vehicle_TA:ReplicatedSteer' in update.keys():
        frames[i]['cars'][player_id]['steer'] = \
            update['TAGame.Vehicle_TA:ReplicatedSteer'] / 255
    if 'TAGame.Vehicle_TA:bReplicatedHandbrake' in update.keys():
        # print('drift')
        frames[i]['cars'][player_id]['drift'] = \
            update['TAGame.Vehicle_TA:bReplicatedHandbrake']
    if 'TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera' in update.keys():
        print('2nd_cam')
        frames[i]['cars'][player_id]['2nd_cam'] = \
            update['TAGame.CameraSettingsActor_TA:bUsingSecondaryCamera']
    if 'TAGame.Vehicle_TA:bDriving' in update.keys():
        # print('driving')
        frames[i]['cars'][player_id]['driving'] = \
            update['TAGame.Vehicle_TA:bDriving']
    if 'TAGame.Car_TA:ReplicatedDemolish' in update.keys():
        frames[i]['cars'][player_id]['demolition'] = \
            update['TAGame.Car_TA:ReplicatedDemolish']
    if 'TAGame.VehiclePickup_TA:ReplicatedPickupData' in update.keys():
        frames[i]['cars'][player_id]['boost_pickup'] = True


def update_player_data(update, frames, i, actor_id):
    if 'Engine.PlayerReplicationInfo:Ping' in update.keys():
        frames[i]['cars'][actor_id]['ping'] = \
            update['Engine.PlayerReplicationInfo:Ping']
    if 'TAGame.PRI_TA:MatchScore' in update.keys():
        frames[i]['cars'][actor_id]['scoreboard']['score'] = \
            update['TAGame.PRI_TA:MatchScore']
    if 'TAGame.PRI_TA:MatchGoals' in update.keys():
        frames[i]['cars'][actor_id]['scoreboard']['goals'] = \
            update['TAGame.PRI_TA:MatchGoals']
        frames[i]['ball']['last_hit'] = None
    if 'TAGame.PRI_TA:MatchAssists' in update.keys():
        frames[i]['cars'][actor_id]['scoreboard']['assists'] = \
            update['TAGame.PRI_TA:MatchAssists']
    if 'TAGame.PRI_TA:MatchSaves' in update.keys():
        frames[i]['cars'][actor_id]['scoreboard']['saves'] = \
            update['TAGame.PRI_TA:MatchSaves']
    if 'TAGame.PRI_TA:MatchShots' in update.keys():
        frames[i]['cars'][actor_id]['scoreboard']['shots'] = \
            update['TAGame.PRI_TA:MatchShots']


def update_ball_data(update, frames, i):
    from player.parser.parser.location import \
        parse_loc_update, parse_rot_update, parse_sleep_update

    if 'TAGame.Ball_TA:HitTeamNum' in update.keys():
        frames[i]['ball']['last_hit'] = update['TAGame.Ball_TA:HitTeamNum']
    if 'TAGame.RBActor_TA:ReplicatedRBState' in update.keys():
        loc = parse_loc_update(update)
        rot = parse_rot_update(update)
        sleep = parse_sleep_update(update)
        if loc:
            frames[i]['ball']['loc'].update(loc)
        if rot:
            frames[i]['ball']['rot'].update(rot)
        if sleep:
            frames[i]['ball']['sleep'] = sleep


def update_boost_data(update, frames, current_car_objects,
                      current_boost_objects, i):
    actor_id = update['Id']

    # Find updated boost values
    if 'TAGame.CarComponent_TA:Vehicle' in update:
        car_id = update['TAGame.CarComponent_TA:Vehicle']['ActorId']

        for player_id in current_boost_objects:
            if car_id == current_car_objects[player_id] and \
                    car_id not in current_boost_objects[player_id]:
                current_boost_objects[player_id].append(update['Id'])

    if 'TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount' in update:
        for player_id in current_boost_objects:
            if actor_id in current_boost_objects[player_id]:
                frames[i]['cars'][player_id]['boost'] = \
                    update['TAGame.CarComponent_Boost_TA:'
                           'ReplicatedBoostAmount'] / 255

    if 'TAGame.CarComponent_TA:Active' in update:
        for player_id in current_boost_objects:
            if actor_id in current_boost_objects[player_id]:
                frames[i]['cars'][player_id]['boosting'] = update[
                    'TAGame.CarComponent_TA:Active']
