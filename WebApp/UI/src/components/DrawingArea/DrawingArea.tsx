import assert from 'assert';
import React from 'react';
import './DrawingArea.css';


class DrawingArea extends React.Component {
    div = React.createRef<HTMLDivElement>()
    svg = React.createRef<SVGSVGElement>()

    box = {left: -1000, top: -1000, right: 1000, bottom: 1000}
    ticksep = 20

    render() {
        return (
            <div ref={this.div} className="drawingArea">
                <svg ref={this.svg} xmlns="http://www.w3.org/2000/svg" viewBox="-1000 -1000 2000 2000">
                    {this.renderGrid()}
                </svg>
            </div>
        )
    }

    componentDidMount() {
        this.scrollCenter();
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
                <path className='tick' d={`M${left},${y} L${right},${y}`}/>)}
            {xticks.map(x =>
                <path className='tick' d={`M${x},${top} L${x},${bottom}`}/>)}
            <path className='axis' d={`M${left},0 L${right},0`}/>
            <path className='axis' d={`M0,${top} L0,${bottom}`}/>
        </g>);
    }

    _mkticks(from: number, to: number, sep: number) {
        return new Array(Math.floor((to - from) / sep)).fill(0)
            .map((_,i) => from + (i + 1) * sep).filter(x => x != 0);
    }
}


type DrawingAreaProps = {

}


export { DrawingArea }