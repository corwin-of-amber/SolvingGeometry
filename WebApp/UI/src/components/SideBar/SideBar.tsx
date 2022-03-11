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

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        e.preventDefault();
        setUserRules(e.target.value);
    }

    return (
        <div className='sidebar'>
            <div className="user-input">
                <h3 className="user-input-title">Please insert rules:</h3>
                <TextField
                    id="user-input-textfield"
                    label="Your Rules"
                    placeholder='Insert rules here'
                    multiline
                    rows={10}
                    onChange={handleChange}/>
                <div className='solve-buttons'>
                    <Tooltip title="Add points to model" arrow>
                        <Button onClick={() => {alert('clicked');}} style={{backgroundColor:"white"}} variant="outlined">Compile</Button>
                    </Tooltip>
                    <div style={{width:"20px"}}></div>
                    <Tooltip title="Solve the problem" arrow>
                        <Button onClick={() => {alert('clicked');}} variant="contained">Solve</Button>
                    </Tooltip>
                </div>
                
            </div>
            <div className="partial-prog">
                <h3 className="partial-prog-title">Program Steps:</h3>
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