import json
import copy
import math
from player.parser.replay_data import Player, Match, Car, Team, Event, Car, Ball, Actor

from collections import defaultdict
from datetime import datetime




def create_match(filename):
    
    with open(filename) as data_file:
        data = json.load(data_file)
    
    metadata = data['Properties']
    match = get_match_data(metadata)

    add_players(match, metadata)
    add_frames(match, data['Frames'])
    
    return match
    print('end')

def get_match_data(metadata):
    
    match = Match()
    
    match.team_size = metadata['TeamSize']
    if 'Team0Score' in metadata:
        match.team_blue_score = metadata['Team0Score']
    else:
        match.team_blue_score = 0
    if 'Team1Score' in metadata:
        match.team_red_score = metadata['Team1Score']
    else:
        match.team_red_score = 0
    match.record_fps = metadata['RecordFPS']
    match.id = metadata['Id']
    match.date_time = metadata['Date'],
    match.num_frames = metadata['NumFrames']
    match.map_name = metadata['MapName']
    try:
        match.date_time = datetime.strptime(match.date_time[0], '%Y-%m-%d %H-%M-%S')
    except ValueError:
        match.date_time = datetime.strptime(match.date_time[0], '%Y-%m-%d:%H-%M')

    return match

def add_players(match, metadata):
    
    players = {}
    
    for player_data in metadata['PlayerStats']:
        player = Player()
        player.name = player_data['Name']
        player.online_id = player_data['OnlineID']
        player.team = player_data['Team']
        player.score = player_data['Score']
        player.goals = player_data['Goals']
        player.assists = player_data['Assists']
        player.saves = player_data['Saves']
        player.shots = player_data['Shots']
        players.update({player.name: player})
    
    match.players = players
    match.cars = {}
    match.ball = Ball()
    match.teams = {}
    match.actors = {}
    return 
        
def add_frames(match, frames_data):
    
    frames = []
    
    for index, frame_data in enumerate(frames_data):
        
        frame = {}
        match.duration = frame_data['Time']
        frame['Time'] = frame_data['Time']

        for car_id in match.cars.keys():
            match.cars[car_id].boost_pickup = False
        
                # Check for deleted actors
        for actor_id in frame_data['DeletedActorIds']:
            if actor_id == match.ball.id:
                match.ball = Ball()
                match.ball.id = None
            if actor_id in match.cars:
                match.cars.pop(actor_id, None)
        
        for actor_update in frame_data['ActorUpdates']:
            
            if 'ClassName' not in actor_update:
                if 'TAGame.PRI_TA:MatchSaves' in actor_update:
                    match.actors[actor_update['Id']].scoreboard['saves'] = actor_update['TAGame.PRI_TA:MatchSaves']
                if 'TAGame.PRI_TA:MatchScore' in actor_update:
                    match.actors[actor_update['Id']].scoreboard['score'] = actor_update['TAGame.PRI_TA:MatchScore']
                    print('TAGame.PRI_TA:MatchScore old: {} new score: {}'.format(actor_update['Id'], actor_update['TAGame.PRI_TA:MatchScore']))
                if 'TAGame.PRI_TA:MatchAssists' in actor_update:
                    match.actors[actor_update['Id']].scoreboard['assists'] = actor_update['TAGame.PRI_TA:MatchAssists']
                if 'TAGame.PRI_TA:MatchShots' in actor_update:
                    match.actors[actor_update['Id']].scoreboard['shots'] = actor_update['TAGame.PRI_TA:MatchShots']
                if 'TAGame.PRI_TA:MatchGoals' in actor_update:
                    match.actors[actor_update['Id']].scoreboard['goals'] = actor_update['TAGame.PRI_TA:MatchGoals']

                if 'Engine.TeamInfo:Score' in actor_update:
                    match.teams[actor_update['Id']].score = actor_update['Engine.TeamInfo:Score']
                if 'TAGame.RBActor_TA:ReplicatedRBState' in actor_update:
                    id = actor_update['Id']
                    if id == match.ball.id:
                        update_car_or_ball_state(match.ball, actor_update)
                    if id in match.cars:
                        update_car_or_ball_state(match.cars[id], actor_update)

                if 'TAGame.Car_TA:ReplicatedDemolish' in actor_update:
                    get_car(match, actor_update).demolition = True

            else:
                if 'TAGame.Team_Soccar_TA' == actor_update['ClassName']:
                   add_team(match, actor_update)
                
                elif 'TAGame.Car_TA' == actor_update['ClassName']:
                    if 'Engine.Pawn:PlayerReplicationInfo' in actor_update:
                        
                        print('Engine.Pawn:PlayerReplicationInfo old: {} new: {}'.format(actor_update['Engine.Pawn:PlayerReplicationInfo']['ActorId'], actor_update['Id']))
                        
                        actor_id = actor_update['Engine.Pawn:PlayerReplicationInfo']['ActorId']
                        if actor_id in match.actors:
                            actor = match.actors[actor_update['Engine.Pawn:PlayerReplicationInfo']['ActorId']]
                        else:
                            actor = Actor()
                            match.actors[actor_id] = actor
                        if actor_update['Id'] in match.cars:
                            actor.car = match.cars[actor_update['Id']]
                        else:
                            match.cars[actor_update['Id']] = get_car(match, actor_update)
                            actor.car = match.cars[actor_update['Id']]
                    car = get_car(match, actor_update)
                    update_car_or_ball_state(car, actor_update)
                    
                
                elif 'TAGame.Ball_TA' == actor_update['ClassName']:
                    ball_id = actor_update['Id']
                    if not hasattr(match.ball, 'id') or ball_id != match.ball.id:
                         match.ball = Ball()
                         match.ball.id = ball_id
                    update_car_or_ball_state(match.ball, actor_update)
                
                elif 'TAGame.PRI_TA' == actor_update['ClassName']:
                   
                    actor_id = actor_update['Id']
                    
                    actors = match.actors
                    
                    if actor_id not in actors:
                        actors[actor_id] = Actor()
                        actors[actor_id].car = get_car(match, actor_update)
                    if 'Engine.PlayerReplicationInfo:PlayerName' in actor_update:
                        actors[actor_id].name = actor_update['Engine.PlayerReplicationInfo:PlayerName']
                    if 'Engine.PlayerReplicationInfo:Team' in actor_update:
                        actors[actor_id].team =  actor_update['Engine.PlayerReplicationInfo:Team']['ActorId']
                    elif 'ClassName' in actor_update and actor_update['ClassName'] == 'TAGame.Team_Soccar_TA':
                        if actor_update['TypeName'] == 'Archetypes.Teams.Team0':
                            match.teams[actor_update['Id']].color = 'blue'
                        elif actor_update['TypeName'] == 'Archetypes.Teams.Team1':
                            match.teams[actor_update['Id']].color = 'red'

                if 'TAGame.VehiclePickup_Boost_TA' == actor_update['ClassName'] and 'TAGame.VehiclePickup_TA:ReplicatedPickupData' in actor_update:
                    actor_update['Id'] = actor_update['TAGame.VehiclePickup_TA:ReplicatedPickupData']['ActorId']
                    car = get_car(match, actor_update)
                    car.boost_pickup = True

        for actor_id in match.actors:
            
            car = match.actors[actor_id].car
            
            car.dist_ball = calc_dist(car, match.ball)
            if car.dist_ball is not None and car.dist_ball < 300 and match.duration - car.lasthit >= 1:
                car.hit = True
                match.actors[actor_id].scoreboard['hits'] = match.actors[actor_id].scoreboard['hits'] + 1
                car.lasthit = match.duration
            else:
                car.hit = False

        new_frame = build_frame(match)
        frames.append(new_frame)
    match.json = frames

def build_frame(match):
    
    frame = {}
    frame['time'] = match.duration
    frame['cars'] = {}
    frame['ball'] = {}
    frame['teams'] = {}

    min_car_dist = float("inf")

    ball = match.ball 

    for actor_id in match.actors:
        car = copy.deepcopy(match.actors[actor_id].car)
        car.scoreboard = copy.deepcopy(match.actors[actor_id].scoreboard)
        car.name = match.actors[actor_id].name
        frame['cars'][ match.actors[actor_id].name] = car.__dict__
    
    frame['ball'] = copy.deepcopy(ball).__dict__
    
    for team in match.teams:
        frame['teams'][match.teams[team].color] = {'score' : match.teams[team].score}
        
    return frame

def calc_dist(actor1, actor2):
    if not(hasattr(actor1, 'position') and hasattr(actor2, 'position')):
        return None
    return  round(math.sqrt((actor1.position['X']-actor2.position['X'])**2 + (actor1.position['Y']-actor2.position['Y'])**2+ (actor1.position['Z']-actor2.position['Z'])**2))

def update_cars(cars, actor_update):
    
    if 'TAGame.CarComponent_TA:Vehicle' not in actor_update:
        return
    
    class_name = actor_update['ClassName']
    actor_id = actor_update['TAGame.CarComponent_TA:Vehicle']['ActorId']
    
    if actor_id not in cars:
        cars.update({actor_id: get_car(match, actor_update)})
    
    car = cars[actor_id]
    
    if class_name == 'TAGame.CarComponent_Jump_TA':
        car.pos = actor_update['InitialPosition']
    
    return cars

def get_car(match, actor_update):
    id = actor_update['Id']
    if id not in match.cars:
        match.cars[id] = Car()
        match.cars[id].dist_ball = None
        match.cars[id].lasthit = 0
        match.cars[id].demolition = False
        match.cars[id].boost_pickup = False
    return match.cars[id]

def update_car_or_ball_state(car_or_ball, actor_update):
    if 'TAGame.RBActor_TA:ReplicatedRBState' in actor_update:
        state = actor_update['TAGame.RBActor_TA:ReplicatedRBState']
        if 'Position' in state:
            car_or_ball.position = state['Position']
        if 'Rotation' in state:
            car_or_ball.rotation= state['Rotation']
        if 'LinearVelocity' in state:
            car_or_ball.linear_velocity = state['LinearVelocity']
        if 'AngularVelocity' in state:
            car_or_ball.angular_velocity = state['AngularVelocity']
        if 'Sleeping' in state:
            car_or_ball.sleeping = state['Sleeping']

def add_team(match, actor_update):
    
    id = actor_update['Id']
    if 'Archetypes.Teams.Team0' == actor_update['TypeName']:
        match.teams[id] = Team()
        match.teams[id].color = 'blue'
        match.teams[id].score = 0
    elif 'Archetypes.Teams.Team1' == actor_update['TypeName']:
        match.teams[id] = Team()
        match.teams[id].score = 0
        match.teams[id].color = 'red'