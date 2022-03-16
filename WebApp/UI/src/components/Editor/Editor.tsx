import assert from 'assert';
import React from 'react';
import { CodeMirror } from '../../infra/cm6-easy';
import './Editor.css';


class Editor extends React.Component<EditorProps> {
    cmContainer: React.RefObject<HTMLDivElement>
    cm?: CodeMirror

    constructor(props: EditorProps) {
        super(props);
        this.cmContainer = React.createRef();
    }

    render() {
        return <div className="editor-container" ref={this.cmContainer}></div>;
    }

    componentDidMount(): void {
        var div = this.cmContainer.current;
        assert(div)
        this.cm = new CodeMirror(div);
        this.cm.on('change', () => Promise.resolve().then(() =>
            this.props.onChange({value: this.cm!.getValue()})));
    }
}

type EditorProps = { onChange: (ev: {value: string}) => void };


export { Editor }