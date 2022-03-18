import React, { useState, useEffect } from 'react';
import './SideBar.css';
import Button from '@mui/material/Button';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import { FixedSizeList, ListChildComponentProps } from "react-window";
import AutoSizer from "react-virtualized-auto-sizer";
import Tooltip from '@mui/material/Tooltip';
import { Editor } from '../Editor/Editor'; 
import { ListOfSamples } from '../ListOfSamples/ListOfSamples';
import { LabeledPoint, Shapes } from '../DrawingArea/Shapes';


function renderRow(props: ListChildComponentProps) {
    const { index, style } = props;
  
    return (
      <ListItem style={style} key={index} component="div" disablePadding>
        <ListItemButton>
            <ListItemText primary={JSON.stringify(props.data[index])}></ListItemText>
        </ListItemButton>
      </ListItem>
    );
}

class SideBar extends React.Component<SideBarProps, SideBarState> {

    editor = React.createRef<Editor>()
    listOfSamples = React.createRef<ListOfSamples>()

    readonly DEFAULT_SAMPLE = "triangle"

    constructor(props: {}) {
        super(props);
        this.state = {
            userRules: '',
            samples: {},
            sampleNames: [],
            parsedInput: [],
            progSteps: []
        };
    }


    handleChange = (e: {value: string}) => {
        this.setState({userRules: e.value});
    }

    handleCompile = async () => {
        console.log('compile', this.state.userRules);
        var compiled = await this.compileText(this.state.userRules);
        this.setState({parsedInput: compiled.statements});
        this.extractPoints(compiled.statements);
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
            this.editor.current?.open(sample.join('\n'));
    }

    async compileText(programText: string) {
        var r = await fetch('/compile', {method: 'POST', body: programText});
        if (!r.ok) throw r;
        return await r.json();
    }

    /** @todo this logic belongs in `MainContent` */
    extractPoints(statements: Statement[]) {
        var pts = statements.map(stmt => {
            if (stmt.predicate === 'known') {
                var [label, value] = stmt.vars;
                if (typeof label === 'string' && value.$type === 'Point2D')
                    return {
                        label,
                        at: {x: +value.x, y: +value.y}
                    };
            }
        }).filter(x => x) as LabeledPoint[];
        console.log(pts);
        this.props.onShapesReceived?.({points: pts});
    }

    async componentDidMount() {
        await this.getSamples();
        this.listOfSamples.current?.switchTo(this.DEFAULT_SAMPLE);
        this.handleCompile();
    }

    render() {
        let items = this.state.parsedInput;

        return (
            <div className='sidebar'>
                <div className="user-input">
                    <h3 className="user-input-title">
                        Problem Constraints
                        <ListOfSamples ref={this.listOfSamples}
                            sampleNames={this.state.sampleNames}
                            onSelect={name => this.openSample(name)}/>
                    </h3>
                    <Editor ref={this.editor} onChange={this.handleChange}/>
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
                                itemCount={items.length}
                                itemData={items}
                                itemSize={35}
                                overscanCount={5}
                                width={width}>
                                {p => renderRow(p)}
                            </FixedSizeList>
                            )}
                        </AutoSizer>
                    </div>
                </div>
            </div>
        );
    }
}

type SideBarProps = {
    onShapesReceived?: (shapes: Shapes) => void
}

type SideBarState = {
    userRules: string
    samples: {[name: string]: any}
    sampleNames: string[]
    parsedInput: any[],
    progSteps: any[]
}

type Statement = {predicate: string, vars: any[]}


export { SideBar }