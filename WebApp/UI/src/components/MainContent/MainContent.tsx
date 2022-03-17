import React, { useEffect, useState } from 'react';
import './MainContent.css';
import { DrawingArea } from '../DrawingArea/DrawingArea';
import { SideBar } from '.././SideBar/SideBar';


export const MainContent = () => {
    
    return (
        
        <div className="main-content-container">
            <SideBar/>
            <DrawingArea/>
        </div>
        
    )
}