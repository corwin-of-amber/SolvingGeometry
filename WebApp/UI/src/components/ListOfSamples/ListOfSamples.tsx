import React, { ChangeEvent, useState } from 'react';


export const ListOfSamples = (props: ListOfSamplesProps) => {
    const handleChange = (ev: ChangeEvent<HTMLSelectElement>) => {
        props.onSelect?.(ev.target.value);
    }
    return (
        <select onChange={handleChange}>
            {props.sampleNames.map((name: string) => <option key={name} value={name}>{name}</option>)}
        </select>
    );
}

type ListOfSamplesProps = { sampleNames: string[], onSelect?: (name: string) => void };