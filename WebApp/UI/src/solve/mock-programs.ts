import Flatten from '@flatten-js/core';
import { MiniProgram, SearchRange } from './mini-solve';


const MOCK_TRIANGLE = (known: MiniProgram.Env) => {
    if (['X', 'Z'].every(k => known[k])) {
        let c1 = c(known).circ('X', 'Z'),
            c2 = c(known).circ('Z', 'X');

        return new MiniProgram([
                [0, 'Y', _ => c1.intersect(c2)],
                {draw: env => c(env).segs(['XY', 'YZ', 'XZ'])}
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
                [1, 'C', env => c(env).onCirc('B', dist, 'C')],
                [0, 'D', env => c(env).circ('C', dist)
                                    .intersect(c(env).circ('A', dist))],
                {draw: env => c(env).segs(['AB', 'BC', 'CD', 'AD'])}
            ],
            env =>
                (c(env).len('AD') < 1 ? 10 : 0) + // penalty
                (c(env).len('DB') < 1 ? 10 : 0) + // penalty
                Math.abs(c(env).len('AC') - c(env).len('BD'))
        );   
    }
    else throw new MiniProgram.MissingInputs();
}

const MOCK_SQUARE_IN_SQUARE = (known: MiniProgram.Env) => {
    if (['A', 'B'].every(k => known[k])) {
        return new MiniProgram([
                MOCK_SQUARE,
                ienv => new MiniProgram([
                    [1, 'E', env => c(env).onSeg('AB', 'E')]
                ], env => env['E'].distanceTo(ienv['E'] ?? c(env).seg('AB').middle().translate(Flatten.vector(-10, 0)))[0]),
                [1, 'F', env => c(env).onSeg('BC', 'F')],
                [0, 'G', env => c(env).circ('F', 'E').intersect(c(env).seg('CD'))],
                [0, 'H', env => c(env).circ('G', c(env).len('EF'))
                                    .intersect(c(env).seg('AD'))],
                {draw: env => c(env).segs(['EF', 'FG', 'GH', 'EH'])}
            ], env => Math.abs(c(env).len('EF') - c(env).len('EH'))
        );   
    }
    else throw new MiniProgram.MissingInputs();
}


type Env = MiniProgram.Env;

class Context {
    constructor(public env: Env) { }

    seg([a, b]: string | [string, string]) {
        return Flatten.segment(this.env[a], this.env[b]);
    }

    segs(abs: (string | [string, string])[]) {
        return abs.map(ab => this.seg(ab));
    }

    circ(o: string, a_or_r: string | number) {
        return Flatten.circle(this.env[o], typeof a_or_r === 'number' ? a_or_r
            : this.len([a_or_r, o]));
    }

    len([a, b]: string | [string, string]) {
        return this.env[a].distanceTo(this.env[b])[0];
    }

    onSeg(ab: string | [string, string], around?: string) {
        return SearchRange.segmentAroundPoint_maybe(this.seg(ab),
            around ? this.env[around] : undefined);
    }

    onCirc(o: string, a_or_r: string | number, around?: string) {
        return SearchRange.circleAroundPoint_maybe(this.circ(o, a_or_r),
            around ? this.env[around] : undefined);
    }
}

function c(env: Env) { return new Context(env); }


export default {
    triangle: MOCK_TRIANGLE,
    square: MOCK_SQUARE,
    'square-in-square': MOCK_SQUARE_IN_SQUARE
} as {[name: string]: MiniProgram.Expr<MiniProgram>}