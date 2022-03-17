import React, { useEffect, useState } from 'react';
import './MainContent.css';
import { DrawingArea } from '../DrawingArea/DrawingArea';
import { SideBar } from '../SideBar/SideBar';
import { LabeledPoint } from '../DrawingArea/Shapes';


export const MainContent = () => {
    
    var [points, setPoints] = React.useState<LabeledPoint[]>([
        {label: "X", at: {x: 0, y: 0}},
        {label: "Z", at: {x: 136, y: 0}}
    ]);

    return (
        
        <div className="main-content-container">
            <SideBar/>
            <DrawingArea points={points}/>
        </div>
        
    )
}