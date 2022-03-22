import assert from 'assert';
import _ from 'lodash';
import Flatten from '@flatten-js/core';
import type { LabeledPoint } from './components/DrawingArea/Shapes';


class MiniInterp {
    eval(inputPoints: PointSet) {
        var known = this._import(inputPoints);

        if (['X', 'Z'].every(k => inputPoints[k])) {
            let x = known['X'], z = known['Z'], d = x.distanceTo(z)[0],
                c1 = Flatten.circle(x, d),
                c2 = Flatten.circle(z, d);

            var sol = c1.intersect(c2);

            return this._export({
                'Y': sol[0]
            });
        }
        else if (['A', 'B'].every(k => inputPoints[k])) {
            var a = known['A'], b = known['B'], dist = a.distanceTo(b)[0];
                

            let prog: Instruction[] = [
                [1, 'C', (env: Env) => 
                            this._searchOnCircleAroundPoint_maybe(
                                Flatten.circle(env['B'], dist), env['C'])],
                [0, 'D', (env: Env) =>
                            Flatten.circle(env['C'], dist)
                                .intersect(Flatten.circle(env['A'], dist))]
            ];
            let objective = (pts: Env) =>
                (pts.D.distanceTo(pts.A)[0] < 1 ? 10 : 0) + // penalty
                (pts.D.distanceTo(pts.B)[0] < 1 ? 10 : 0) + // penalty
                Math.abs(pts.A.distanceTo(pts.C)[0] - pts.B.distanceTo(pts.D)[0]);
        
            var candidates = this._compile(prog)(known)
                    .map(env => ({values: env, err: objective(env)}));
            var minimal = _.minBy(candidates, oc => oc.err);

            assert(minimal);

            return this._export(minimal.values);
        }
        else return {};
    }

    _import(ps: PointSet): PointSet<Flatten.Point> {
        return mapValues(ps, v => Flatten.point(v.x, v.y));
    }

    _export(ps: PointSet<Flatten.Point>): PointSet {
        return mapValues(ps, v => ({x: v.x, y: v.y}));
    }

    _searchOnCircle(c: Flatten.Circle): SearchRange<Flatten.Point> {
        let p0 = new Flatten.Point(c.pc.x + c.r, c.pc.y);
        return {lo: 0, hi: 2 * Math.PI,
            construct: (angle: number) => p0.rotate(angle, c.pc)}
    }

    _searchOnCircleAroundPoint(c: Flatten.Circle, pt: Flatten.Point): SearchRange<Flatten.Point> {
        let p0 = new Flatten.Point(c.pc.x + c.r, c.pc.y),
            around = new Flatten.Vector(c.pc, pt).slope;
        return {lo: around - 0.5, hi: around + 0.5,
            construct: (angle: number) => p0.rotate(angle, c.pc)}
    }

    _searchOnCircleAroundPoint_maybe(c: Flatten.Circle, pt?: Flatten.Point): SearchRange<Flatten.Point> {
        return pt ? this._searchOnCircleAroundPoint(c, pt) : this._searchOnCircle(c);
    }

    _slice(sr: SearchRange<Flatten.Point>, nSlices: number = 1000) {
        return _.range(sr.lo, sr.hi, (sr.hi - sr.lo) / nSlices)
            .map(p => sr.construct(p));
    }

    _in0(env: Env, key: string, sr: Locus0, cont: (env: Env) => Env[]) {
        return _.flatten(sr.map(pt => cont({...env, [key]: pt})));        
    }

    _in1(env: Env, key: string, sr: Locus1, cont: (env: Env) => Env[]) {
        return this._in0(env, key, this._slice(sr), cont);
    }

    _bind0(key: string, stmt: (env: Env) => Locus0, cont: (env: Env) => Env[]) {
        return (env: Env) => this._in0(env, key, stmt(env), cont);
    }

    _bind1(key: string, stmt: (env: Env) => Locus1, cont: (env: Env) => Env[]) {
        return (env: Env) => this._in1(env, key, stmt(env), cont);
    }

    _ret() { return (env: Env) => [env]; }

    _compile(instructions: Instruction[]): (env: Env) => Env[] {
        if (instructions.length === 0) return this._ret();
        else {
            var insn = instructions[0], rest = instructions.slice(1);
            switch (insn[0]) {
            case 0:
                return this._bind0(insn[1], insn[2], this._compile(rest));
            case 1:
                return this._bind1(insn[1], insn[2], this._compile(rest));
            default:
                assert(false);
            }
        }
    }
}


function mapValues<T, S>(o: {[key: string]: T}, f: (t: T) => S) {
    return Object.fromEntries(Object.entries(o).map(([k, v]) => [k, f(v)]));
}


export type PointXY = {x: number, y: number};

type PointSet<P extends PointXY = PointXY> = {[name: string]: P};

namespace PointSet {
    export function fromLabeledPoints(points: LabeledPoint[]) {
        return Object.fromEntries(points.map(o => [o.label, o.at]));
    }

    export function toLabeledPoints(points: PointSet) {
        return Object.entries(points).map(([k, v]) => ({label: k, at: v}));
    }
}

type SearchRange<T> = {lo: number, hi: number, construct: (p: number) => T}

type Env = PointSet<Flatten.Point>
type Locus0 = Flatten.Point[]
type Locus1 = SearchRange<Flatten.Point>
type Expr<Locus> = (env: Env) => Locus

type Instruction = [0, string, Expr<Locus0>] | [1, string, Expr<Locus1>]


export { MiniInterp, PointSet }