import React, { useState, useEffect } from 'react';
import './SideBar.css';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import { FixedSizeList, ListChildComponentProps } from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import Tooltip from '@mui/material/Tooltip';
import { Editor } from '../Editor/Editor'; 


function renderRow(props: ListChildComponentProps) {
    const { index, style } = props;
  
    return (
      <ListItem style={style} key={index} component="div" disablePadding>
        <ListItemButton>
          <ListItemText primary={`Item ${index + 1}`} />
        </ListItemButton>
      </ListItem>
    );
}

export const SideBar = () => {

    const [userRules, setUserRules] = useState<string>('');

    const handleChange = (e: {value: string}) => {
        setUserRules(e.value);
    };

    const handleCompile = () => {
        console.log('compile', userRules);
    }

    const handleSolve = () => {
        console.log('solve', userRules);
    }

    return (
        <div className='sidebar'>
            <div className="user-input">
                <h3 className="user-input-title">Problem Constraints</h3>
                <Editor onChange={handleChange}/>
                <div className='solve-buttons'>
                    <Tooltip title="Add points to model" arrow>
                        <Button onClick={handleCompile} style={{backgroundColor:"white"}} variant="outlined">Compile</Button>
                    </Tooltip>
                    <div style={{width:"20px"}}></div>
                    <Tooltip title="Solve the problem" arrow>
                        <Button onClick={handleSolve} variant="contained">Solve</Button>
                    </Tooltip>
                </div>
                
            </div>
            <div className="partial-prog">
                <h3 className="partial-prog-title">Program Steps</h3>
                <div className='partial-prog-output'>
                    <AutoSizer>
                        {({ height, width } : { height:any, width:any }) => (
                        <FixedSizeList
                            className="List"
                            height={height}
                            itemCount={10}
                            itemSize={35}
                            overscanCount={5}
                            width={width}>
                            {renderRow}
                        </FixedSizeList>
                        )}
                    </AutoSizer>
                </div>
            </div>
        </div>
    );
}