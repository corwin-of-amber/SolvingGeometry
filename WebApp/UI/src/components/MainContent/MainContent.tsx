import React, { useEffect, useState } from 'react';
import './MainContent.css';
import { DrawingArea } from '../DrawingArea/DrawingArea';
import { SideBar } from '../SideBar/SideBar';
import { Shapes, LabeledPoint } from '../DrawingArea/Shapes';


export const MainContent = () => {
    
    var [points, setPoints] = React.useState<LabeledPoint[]>([]);

    const handleShapesReceived = (shapes: Shapes) => {
        if (shapes.points) setPoints(shapes.points);
    }

    return (
        
        <div className="main-content-container">
            <SideBar onShapesReceived={handleShapesReceived}/>
            <DrawingArea points={points}/>
        </div>
        
    )
}