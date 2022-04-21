import assert from 'assert';
import React, { ChangeEvent } from 'react';


export class ListOfSamples extends React.Component<ListOfSamplesProps> {

    el = React.createRef<HTMLSelectElement>()

    handleChange = (ev: ChangeEvent<HTMLSelectElement>) => {
        this.props.onSelect?.(ev.target.value);
    }

    switchTo(name: string) {
        var sel = this.el.current;
        assert(sel);
        sel.value = name;
        this.props.onSelect?.(name);
    }

    render() {
        return (
            <select ref={this.el} disabled={this.props.disabled}
                    onChange={this.handleChange}>
                <optgroup label="samples">
                    {this.props.sampleNames.map((name: string) =>
                        <option key={name} value={name}>{name}</option>)}
                </optgroup>
            </select>
        );
    }
}

type ListOfSamplesProps = { sampleNames: string[], onSelect?: (name: string) => void, disabled?: boolean};