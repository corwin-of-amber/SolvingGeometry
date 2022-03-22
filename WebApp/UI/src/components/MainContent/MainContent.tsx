import React from 'react';
import './MainContent.css';
import { DrawingArea } from '../DrawingArea/DrawingArea';
import { SideBar } from '../SideBar/SideBar';
import { Shapes, LabeledPoint } from '../DrawingArea/Shapes';
import { MiniInterp, PointSet } from '../../solve/mini-solve';
import MOCK_PROGRAMS from '../../solve/mock-programs';


class MainContent extends React.Component<{}, MainContentState> {

    interp?: MiniInterp

    constructor(props: {}) {
        super(props);
        this.state = {
            points: []
        };
    }

    solveAndSetPoints(points: LabeledPoint[]) {
        if (this.interp) {
            var pointset = PointSet.fromLabeledPoints(points),
                sol = this.interp.eval(pointset);
            points = PointSet.toLabeledPoints(sol);
        }
        this.setState({points});
    }

    handleShapesReceived = (shapes: Shapes) => {
        if (shapes.points) this.solveAndSetPoints(shapes.points);
    }

    onOpened = (name: string, defs: any) => {
        var mock = MOCK_PROGRAMS[name];
        this.interp = mock ? new MiniInterp(mock) : undefined;
        console.log(this.interp);
    }

    onMovePoint = (pt: LabeledPoint) => {
        this.solveAndSetPoints(this.state.points.map(lpt => pt.label === lpt.label ? pt : lpt));
    }

    render() {
        return (            
            <div className="main-content-container">
                <SideBar onOpened={this.onOpened} onShapesReceived={this.handleShapesReceived}/>
                <DrawingArea points={this.state.points} onMovePoint={this.onMovePoint}/>
            </div>
        )
    }
}


type MainContentState = {points: LabeledPoint[]}


export { MainContent }