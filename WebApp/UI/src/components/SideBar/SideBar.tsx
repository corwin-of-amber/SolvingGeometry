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
import { ListOfSamples } from '../ListOfSamples/ListOfSamples';


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

class SideBar extends React.Component<{}, SideBarState> {

    editorRef: React.RefObject<Editor>

    constructor(props: {}) {
        super(props);
        this.editorRef = React.createRef<Editor>();
        this.state = {
            userRules: '',
            samples: {},
            sampleNames: []
        };
    }


    handleChange = (e: {value: string}) => {
        this.setState({userRules: e.value});
    }

    handleCompile = () => {
        console.log('compile', this.state.userRules);
    }

    handleSolve = () => {
        console.log('solve', this.state.userRules);
    }

    async getSamples() {
        const samples = await (await fetch('/samples')).json();
        try {
            this.setState({samples, sampleNames: Object.keys(samples)});
        }
        catch (e) { console.error('failed to load samples', e); }
    }

    openSample(name: string) {
        var sample = this.state.samples[name];
        if (sample)
            this.editorRef?.current?.open(sample.join('\n'));
    }

    componentDidMount() {
        this.getSamples();
    }

    render() {
        return (
            <div className='sidebar'>
                <div className="user-input">
                    <h3 className="user-input-title">
                        Problem Constraints
                        <ListOfSamples sampleNames={this.state.sampleNames}
                            onSelect={name => this.openSample(name)}/>
                    </h3>
                    <Editor ref={this.editorRef} onChange={this.handleChange}/>
                    <div className='solve-buttons'>
                        <Tooltip title="Add points to model" arrow>
                            <Button onClick={this.handleCompile} style={{backgroundColor:"white"}} variant="outlined">Compile</Button>
                        </Tooltip>
                        <div style={{width:"20px"}}></div>
                        <Tooltip title="Solve the problem" arrow>
                            <Button onClick={this.handleSolve} variant="contained">Solve</Button>
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
}

type SideBarState = {
    userRules: string
    samples: {[name: string]: any}
    sampleNames: string[]
}


export { SideBar }