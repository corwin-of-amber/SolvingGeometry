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
            <g key={label} className="labeledPoint">
                {['stroked', 'fore'].map(cs =>
                    <text key={cs} className={cs} x={x + ofs.x} y={y + ofs.y}>{label}</text>)}
                <circle cx={x} cy={y}/>
            </g>);
    }

    _mkticks(from: number, to: number, sep: number) {
        return new Array(Math.floor((to - from) / sep)).fill(0)
            .map((_,i) => from + (i + 1) * sep).filter(x => x != 0);
    }
}


type DrawingAreaProps = {
    ticksep?: number
    points?: LabeledPoint[]
};


export { DrawingArea }