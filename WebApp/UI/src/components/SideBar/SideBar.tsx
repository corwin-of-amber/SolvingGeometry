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
import { LabeledPoint, Shapes, Segment, PointXY } from '../DrawingArea/Shapes';


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

    readonly DEFAULT_SAMPLE = "square"

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
        this.props.onCompiled?.(compiled.statements);
        this.extractPoints(compiled.statements);
    }

    handleSolve = async () => {
        console.log('solve', this.state.userRules);
        var solution = await this.solveText(this.state.userRules);
        console.log(solution);
        this.parseSolutionPartialProg(solution[0]);

        let points: LabeledPoint[] = []
        const points_keys = Object.keys(solution[1]);
        points_keys.forEach((key, index) => {
            let at:PointXY = {x: Number(solution[1][key][0]), y: Number(solution[1][key][1])}
            let p:LabeledPoint = {label: key, at: at};
            points.push(p);
        });

        console.log(points);
        
        let segments = solution[2].map((seg: string[]) => {
            let start:PointXY = {x: Number(seg[0]), y:Number(seg[1])};
            let end:PointXY = {x: Number(seg[2]), y:Number(seg[3])};
            return {
                start,
                end
            };
        }).filter((x: object) => x) as Segment[];

        console.log(segments);

        this.props.onSolve?.(points, segments);
    }

    parseSolutionPartialProg = (solution:string) => {
        let only_rules = solution.substring(solution.indexOf("rules")+8, solution.indexOf("not_equal")-5);
        console.log(only_rules);
        const final_list = only_rules.split("],\n").map(rawrule => rawrule.substring(2));
        console.log(final_list);
        this.setState({progSteps: final_list});
    }


    // parseSolutionPoints = (obj: any) => {
    //     obj.map(pt => pt);
        
    // }

    async getSamples() {
        const samples = await (await fetch('/samples')).json();
        try {
            this.setState({samples, sampleNames: Object.keys(samples)});
        }
        catch (e) { console.error('failed to load samples', e); }
    }

    openSample(name: string) {
        var sample = this.state.samples[name];
        if (sample) {
            this.editor.current?.open(sample.join('\n'));
            this.props.onOpened?.(name, sample);
        }
    }

    async compileText(programText: string): Promise<{statements: Statement[]}> {
        var r = await fetch('/compile', {method: 'POST', body: programText});
        if (!r.ok) throw r;
        return await r.json();
    }

    async solveText(programText: string): Promise<any> {
        var r = await fetch('/solve', {method: 'POST', body: programText});
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
            return undefined;
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
        let items = this.state.progSteps;

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
    onOpened?: (name: string, defs: any) => void
    onCompiled?: (statements: Statement[]) => void
    onShapesReceived?: (shapes: Shapes) => void
    onSolve?: (points: LabeledPoint[], segments: Segment[]) => void
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