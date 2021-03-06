import {Ball} from './ball.model';
import {Car} from './car.model';
import {ScoreBoard} from './scoreboard.model';

export class Frame {
  time: number;
  ball: Ball;
  teams : number[]
  cars: Car[];
  scoreboard: ScoreBoard;
  color: string;
}
