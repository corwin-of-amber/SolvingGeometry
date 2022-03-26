
export type PointXY = {x: number, y: number};

export type LabeledPoint = {label: string, at: PointXY};

export type Shapes = {
    points: LabeledPoint[]
}

export type Segment = {
    start: PointXY,
    end: PointXY
}