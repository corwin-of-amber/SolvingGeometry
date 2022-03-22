import assert from 'assert';
import React from 'react';
import { Pan, Zoom } from '../../infra/ui-pan-zoom';
import { LabeledPoint } from './Shapes';
import './DrawingArea.css';


class DrawingArea extends React.Component<DrawingAreaProps> {
    div = React.createRef<HTMLDivElement>()
    svg = React.createRef<SVGSVGElement>()

    box = {left: -1000, top: -1000, right: 1000, bottom: 1000}
    ticksep = 20
    labelOffset = {x: -7, y: 1}

    panner?: Pan
    zoomer?: Zoom

    constructor(props: DrawingAreaProps) {
        super(props);
        if (props.ticksep) this.ticksep = props.ticksep;
    }

    render() {
        return (
            <div ref={this.div} className="drawingArea">
                <svg ref={this.svg} xmlns="http://www.w3.org/2000/svg" viewBox="-1000 -1000 2000 2000">
                    {this.renderGrid()}
                    <g className="diagram">
                        {this.renderPoints(this.props.points)}
                    </g>
                </svg>
            </div>
        )
    }

    componentDidMount() {
        this.scrollCenter();
        this.panner = new Pan(this.div.current!);
        this.zoomer = new Zoom(this.div.current!);
        this.zoomer.setZoom = z =>
            this.svg.current!.style.width = `${(this.box.right - this.box.left) * z}px`;
    }

    scrollCenter() {
        var div = this.div.current;
        assert(div);
        var box = div.getBoundingClientRect();
        div.scrollLeft = (div.scrollWidth - box.width) / 2;
        div.scrollTop = (div.scrollHeight - box.height) / 2;
    }

    renderGrid() {
        var {left, right, top, bottom} = this.box, sep = this.ticksep,            
            xticks = this._mkticks(left, right, sep),
            yticks = this._mkticks(top, bottom, sep);
        return (<g className="grid">
            {yticks.map(y =>
                <path key={y} className='tick' d={`M${left},${y} L${right},${y}`}/>)}
            {xticks.map(x =>
                <path key={x} className='tick' d={`M${x},${top} L${x},${bottom}`}/>)}
            <path className='axis' d={`M${left},0 L${right},0`}/>
            <path className='axis' d={`M0,${top} L0,${bottom}`}/>
        </g>);
    }

    renderPoints(points: LabeledPoint[] = []) {
        var ofs = this.labelOffset;
        return points.map(({label, at: {x, y}}) =>
            <g key={label} className="labeledPoint mobile"
                        onPointerDownCapture={ev => this.pointDrag.start(ev, label)}
                        onPointerMove={ev => this.pointDrag.move(ev, label)}
                        onPointerUp={ev => this.pointDrag.end(ev, label)}>
                {['stroked', 'fore'].map(cs =>
                    <text key={cs} className={cs} x={x + ofs.x} y={-y + ofs.y}>{label}</text>)}
                <circle cx={x} cy={-y}/>
            </g>);
    }

    pointDrag = new DrawingAreaGesture(this)

    _mkticks(from: number, to: number, sep: number) {
        return new Array(Math.floor((to - from) / sep)).fill(0)
            .map((_,i) => from + (i + 1) * sep).filter(x => x !== 0);
    }
}


class DrawingAreaGesture {
    active?: PointDragGesture

    constructor(private drawingArea: DrawingArea) { }

    start(ev: React.PointerEvent, label: string) {
        this.active = PointDragGesture.start(ev, label, this.drawingArea);
    }
    move(ev: React.PointerEvent, label: string) {
        this.active?.move(ev, label);
    }
    end(ev: React.PointerEvent, label: string) {
        this.active?.end(ev, label);
        this.active = undefined;
    }
}


class PointDragGesture {
    svg: SVGSVGElement
    start: PointXY
    initial: LabeledPoint
    hook: (pt: LabeledPoint) => void

    constructor(svg: SVGSVGElement, start: PointXY, initial: LabeledPoint, hook: (pt: LabeledPoint) => void) {
        this.svg = svg;
        this.start = start;
        this.initial = initial;
        this.hook = hook;
    }

    static start(ev: React.PointerEvent, label: string, drawingArea: DrawingArea) {
        let pt = drawingArea.props.points?.find(pt => pt.label === label);
        if (pt) {
            (ev.target as Element).setPointerCapture(ev.pointerId);
            ev.stopPropagation();
            return new PointDragGesture(
                drawingArea.svg.current!,
                {x: ev.clientX, y: ev.clientY}, 
                pt, drawingArea.props.onMovePoint!);
        }
    }

    move(ev: React.PointerEvent, label: string) {
        let delta = scaleDOMToSVG(this.svg, {x: ev.clientX - this.start.x, y: ev.clientY - this.start.y}),
            o = this.initial;
        this.hook({label: o.label, at: {x: o.at.x + delta.x, y: o.at.y - delta.y}});
    }

    end(ev: React.PointerEvent, label: string) {
        (ev.target as Element).releasePointerCapture(ev.pointerId);
    }
}


type DrawingAreaProps = {
    ticksep?: number
    points?: LabeledPoint[]
    onMovePoint?: (pt: LabeledPoint) => void
};

type PointXY = {x: number, y: number}

/* auxiliary function for translating coordinates when zoomed in or out */
function scaleDOMToSVG(svg: SVGSVGElement, xy: PointXY) {
    var matrix = svg.getCTM();
    assert(matrix);
    return {x: xy.x / matrix.a, y: xy.y / matrix.d};
}


export { DrawingArea }