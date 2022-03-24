import assert from 'assert';
import _ from 'lodash';
import Flatten from '@flatten-js/core';
import type { LabeledPoint } from '../components/DrawingArea/Shapes';


class MiniInterp {
    prog: Expr<MiniProgram>

    constructor(prog: Expr<MiniProgram>) {
        this.prog = prog;
    }

    eval(inputPoints: PointSet) {
        var known = this._import(inputPoints);
        try {
            var prog = this.prog(known);
        }
        catch (e) {
            if (e instanceof MiniProgram.MissingInputs)
                return known;
            else throw e;
        }


        return this._export(this.solve(prog, known)[0]);
    }

    solve(prog: MiniProgram, env: Env) {
        var candidates = this._compile(prog.stmts)(env)
                .map(env => ({values: env, err: prog.objfunc(env)}));
        var minimal = _.minBy(candidates, oc => oc.err);

        assert(minimal);

        return [minimal.values];
    }

    _import(ps: PointSet): PointSet<Flatten.Point> {
        return mapValues(ps, v => Flatten.point(v.x, v.y));
    }

    _export(ps: PointSet<Flatten.Point>): PointSet {
        return mapValues(ps, v => ({x: v.x, y: v.y}));
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

    _compile(instructions: (Instruction | Continuation)[]): (env: Env) => Env[] {
        if (instructions.length === 0) return this._ret();
        else {
            var insn = instructions[0], rest = instructions.slice(1);
            if (insn instanceof Function) {
                var finsn = insn as Function, cont = this._compile(rest);
                return env => _.flatten(this.solve(finsn(env), env)
                               .map(env => cont(env)));
            }
            else {
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

namespace SearchRange {

    export function pointOptional<T, A, S>(withoutArg: (t: T) => S, withArg: (t: T, a: A) => S) {
        return (t: T, a?: A) => a ? withArg(t, a) : withoutArg(t);
    }

    export function circle(c: Flatten.Circle): SearchRange<Flatten.Point> {
        let p0 = new Flatten.Point(c.pc.x + c.r, c.pc.y);
        return {lo: 0, hi: 2 * Math.PI,
            construct: (angle: number) => p0.rotate(angle, c.pc)}
    }

    export function circleAroundPoint(c: Flatten.Circle, pt: Flatten.Point): SearchRange<Flatten.Point> {
        let p0 = new Flatten.Point(c.pc.x + c.r, c.pc.y),
            around = new Flatten.Vector(c.pc, pt).slope,
            delta = 0.5;
        return {lo: around - delta, hi: around + delta,
            construct: (angle: number) => p0.rotate(angle, c.pc)}
    }

    export const circleAroundPoint_maybe = pointOptional(circle, circleAroundPoint);

    export function segment(seg: Flatten.Segment): SearchRange<Flatten.Point> {
        var vec = Flatten.vector(seg.ps, seg.pe);
        return {lo: 0, hi: 1,
            construct: (p: number) => seg.ps.translate(vec.multiply(p))};
    }

    export function segmentAroundPoint(seg: Flatten.Segment, pt: Flatten.Point): SearchRange<Flatten.Point> {
        var vec = Flatten.vector(seg.ps, seg.pe),
            around = pt.distanceTo(seg.ps)[0] / seg.length,
            delta = 0.1;
        return {lo: Math.max(0, around - delta), hi: Math.min(1, around + delta),
            construct: (p: number) => seg.ps.translate(vec.multiply(p))};
    }

    export const segmentAroundPoint_maybe = pointOptional(segment, segmentAroundPoint);
}

type Env = PointSet<Flatten.Point>
type Locus0 = Flatten.Point[]
type Locus1 = SearchRange<Flatten.Point>
type Expr<Ty> = (env: Env) => Ty

type Instruction = [0, string, Expr<Locus0>] | [1, string, Expr<Locus1>]
type Continuation = Expr<MiniProgram>
type ObjectiveFunction = Expr<number>

class MiniProgram {
    constructor(public stmts: (Instruction | Continuation)[],
        public objfunc: ObjectiveFunction) { }
}

type _Env = Env;
type _Expr<Ty> = Expr<Ty>;

namespace MiniProgram {
    export type Env = _Env;
    export type Expr<Ty> = _Expr<Ty>;

    export class MissingInputs { }
}


export { MiniInterp, PointSet, SearchRange, MiniProgram }