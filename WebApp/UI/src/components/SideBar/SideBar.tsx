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
  
    function sym(sym: string) {
        return (sym === ':in') ? ":\u2208" : sym;
    }

    function renderRule(rule: string | any[]) {
        if (typeof rule === 'string') return rule;  // e.g. 'Solving...'
        try {
            if (rule[0] === 'assert')
                return <span><b>assert</b> {rule[1]}</span>;
            else
                return `${rule[1]} ${sym(rule[0])} ${rule.slice(2).map(x => `${x}`).join(' ')}`;
        }
        catch (e) { console.error(e); return "???"; }
    }

    return (
      <ListItem style={style} key={index} component="div" disablePadding>
        <ListItemButton>
            {renderRule(props.data[index])}
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
            progSteps: [],
            fetching: false
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
        this.setState({fetching: true});
        this.setState({progSteps: ['Solving...']});

        try {
            var response = await this.presolveText(this.state.userRules);
        } catch (error) {
            this.setState({fetching: false});
            this.setState({progSteps: ['Error!']});
            return;
        }
          
        
        console.log(response);
        this.parseSolutionPartialProg(response[0]);

        try {
            var solution = await this.solveText(this.state.userRules);
        }
        catch (error) {
            this.setState({fetching: false});
            console.error(error);
            window.alert('oops! internal error occurred.');
            return;
        }

        let points: LabeledPoint[] = []
        const points_keys = Object.keys(solution[1]);
        points_keys.forEach((key, index) => {
            /** @oops `eval` is needed because numbers are fractions */
            let at:PointXY = {x: eval(solution[1][key][0]), y: eval(solution[1][key][1])}
            let p:LabeledPoint = {label: key, at: at};
            points.push(p);
        });

        console.log(points);
        
        let segments = solution[2].map((seg: string[]) => {
            let start:PointXY = {x: eval(seg[0]), y:eval(seg[1])};
            let end:PointXY = {x: eval(seg[2]), y:eval(seg[3])};
            return {
                start,
                end
            };
        }).filter((x: object) => x) as Segment[];

        console.log(segments);

        this.props.onSolve?.(points, segments);
        this.setState({fetching: false});
    }

    parseSolutionPartialProg = (solution: string[]) => {
        this.setState({progSteps: solution});
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
        if (sample) {
            this.editor.current?.open(sample.join('\n'));
            this.props.onOpened?.(name, sample);
        }
    }

    compileText(programText: string): Promise<{statements: Statement[]}> {
        return this.postText('/compile', programText);
    }
    presolveText(programText: string): Promise<ServerResponse> {
        return this.postText('/presolve', programText);
    }
    solveText(programText: string): Promise<ServerResponse> {
        return this.postText('/solve', programText);
    }

    async postText(path: string, programText: string) {
        var r = await fetch(path, {method: 'POST', body: programText});
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
                            onSelect={name => this.openSample(name)} disabled={this.state.fetching}/>
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
    progSteps: any[],
    fetching: boolean
}

type Statement = {predicate: string, vars: any[]}
type ServerResponse = [string[], {[label: string]: [string, string]}, [string, string, string, string][]]


export { SideBar }