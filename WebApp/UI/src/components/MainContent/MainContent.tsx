import React, { useEffect, useState } from 'react';
import './MainContent.css';
import { DrawingArea } from '../DrawingArea/DrawingArea';
import { SideBar } from '../SideBar/SideBar';
import { Shapes, LabeledPoint } from '../DrawingArea/Shapes';
import { MiniInterp, PointSet } from '../../mini-solve';


class MainContent extends React.Component<{}, MainContentState> {

    constructor(props: {}) {
        super(props);
        this.state = {
            points: []
        };
    }

    solveAndSetPoints(points: LabeledPoint[]) {
        var interp = new MiniInterp(), pointset = PointSet.fromLabeledPoints(points),
            sol = interp.eval(pointset);
        this.setState({points: PointSet.toLabeledPoints({...pointset, ...sol})});
    }

    handleShapesReceived = (shapes: Shapes) => {
        if (shapes.points) this.solveAndSetPoints(shapes.points);
    }

    onMovePoint = (pt: LabeledPoint) => {
        this.solveAndSetPoints(this.state.points.map(lpt => pt.label === lpt.label ? pt : lpt));
    }

    render() {
        return (            
            <div className="main-content-container">
                <SideBar onShapesReceived={this.handleShapesReceived}/>
                <DrawingArea points={this.state.points} onMovePoint={this.onMovePoint}/>
            </div>
        )
    }
}


type MainContentState = {points: LabeledPoint[]}


export { MainContent }