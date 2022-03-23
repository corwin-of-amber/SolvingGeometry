import Flatten from '@flatten-js/core';
import { MiniProgram, SearchRange } from './mini-solve';


const MOCK_TRIANGLE = (known: MiniProgram.Env) => {
    if (['X', 'Z'].every(k => known[k])) {
        let x = known['X'], z = known['Z'], d = x.distanceTo(z)[0],
            c1 = Flatten.circle(x, d),
            c2 = Flatten.circle(z, d);

        return new MiniProgram([
                [0, 'Y', _ => c1.intersect(c2)]
            ],
            _ => 0
        );
    }
    else throw new MiniProgram.MissingInputs();
}

const MOCK_SQUARE = (known: MiniProgram.Env) => {
    if (['A', 'B'].every(k => known[k])) {
        var a = known['A'], b = known['B'], dist = a.distanceTo(b)[0];
            
        return new MiniProgram([
                [1, 'C', env => 
                            SearchRange.circleAroundPoint_maybe(
                                Flatten.circle(env['B'], dist), env['C'])],
                [0, 'D', env =>
                            Flatten.circle(env['C'], dist)
                                .intersect(Flatten.circle(env['A'], dist))]
            ],
            env =>
                (env['D'].distanceTo(env['A'])[0] < 1 ? 10 : 0) + // penalty
                (env['D'].distanceTo(env['B'])[0] < 1 ? 10 : 0) + // penalty
                Math.abs(env['A'].distanceTo(env['C'])[0] - env['B'].distanceTo(env['D'])[0])
        );   
    }
    else throw new MiniProgram.MissingInputs();
}

const MOCK_SQUARE_IN_SQUARE = (known: MiniProgram.Env) => {
    if (['A', 'B'].every(k => known[k])) {
        var a = known['A'], b = known['B'], dist = a.distanceTo(b)[0];
            
        return new MiniProgram([
                MOCK_SQUARE,
                ienv => new MiniProgram([
                    [1, 'E', env => SearchRange.segmentAroundPoint_maybe(Flatten.segment(env['A'], env['B']), env['E']) ]
                ], env => env['E'].distanceTo(ienv['E'] ?? Flatten.segment(env['A'], env['B']).middle())[0]),
                [1, 'F', env => SearchRange.segmentAroundPoint_maybe(Flatten.segment(env['B'], env['C']), env['F']) ],
                [0, 'G', env =>
                    Flatten.circle(env['F'], env['F'].distanceTo(env['E'])[0]).intersect(
                        Flatten.segment(env['C'], env['D']))],
                [0, 'H', env =>
                    Flatten.circle(env['G'], env['F'].distanceTo(env['E'])[0]).intersect(
                        Flatten.segment(env['A'], env['D']))],
            ], env => Math.abs(env['E'].distanceTo(env['F'])[0] - 
                               env['E'].distanceTo(env['H'])[0])
        );   
    }
    else throw new MiniProgram.MissingInputs();
}


export default {
    triangle: MOCK_TRIANGLE,
    square: MOCK_SQUARE,
    'square-in-square': MOCK_SQUARE_IN_SQUARE
} as {[name: string]: MiniProgram.Expr<MiniProgram>}