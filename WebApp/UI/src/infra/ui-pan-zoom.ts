


class PanZoomBase {
    $el: HTMLElement

    setScroll: (xy: PointXY) => void
    getScroll: () => PointXY

    constructor($el: HTMLElement) {
        this.$el = $el;
        this.setScroll = (xy) => {
            this.$el.scrollLeft = xy.x;
            this.$el.scrollTop = xy.y;
        };
        this.getScroll = () => ({x: this.$el.scrollLeft, y: this.$el.scrollTop});
    }
}


class Pan extends PanZoomBase {
    gesture?: {start: PointXY, initialScroll: PointXY}

    constructor($el: HTMLElement) {
        super($el);
        this.$el.addEventListener('pointerdown', (ev) => this.onStart(ev));
        this.$el.addEventListener('pointermove', (ev) => this.onMove(ev));
        this.$el.addEventListener('pointerup', (ev) => this.onEnd(ev));
    }

    onStart(ev: PointerEvent) {
        this.$el.classList.add('panning');
        this.gesture = {
            start: {x: ev.x, y: ev.y},
            initialScroll: this.getScroll()
        };
        this.$el.setPointerCapture(ev.pointerId);
        ev.preventDefault();
    }

    onMove(ev: PointerEvent) {
        if (this.gesture) {
            var {start: o, initialScroll: d} = this.gesture;
            this.setScroll({x: d.x - (ev.x - o.x), y: d.y - (ev.y - o.y)});
            ev.preventDefault();
        }
    }

    onEnd(ev: PointerEvent) {
        this.$el.classList.remove('panning');
        this.gesture = undefined;
        this.$el.setPointerCapture(ev.pointerId);
        ev.preventDefault();
    }
}


class Zoom extends PanZoomBase {
    zoomRange: {min: number, max: number}
    accel: number

    areaOffset: PointXY
    zoom: number
    pscroll: FPointXY

    setZoom: (z: number) => void

    constructor($el: HTMLElement) {
        super($el);
        this.zoomRange = {min: .25, max: 8};
        this.accel = 5;
        this.areaOffset = {x: 0, y: 0};
        this.zoom = 1;
        this.pscroll = {x: 0, y: 0};

        this.setZoom = (z) => { /* no default impl; caller should set this */ };

        this.$el.addEventListener('scroll', () => this.onScroll());
        this.$el.addEventListener('wheel', (ev) => this.onWheel(ev));
    }

    onScroll() {
        var sc = this.getScroll();
        if (sc.x !== Math.round(this.pscroll.x) || sc.y !== Math.round(this.pscroll.y))
            this.pscroll = sc;
    }

    adjustZoom(newValue: number, around: PointXY = {x:0, y:0}) {
        var u = this.zoom, v = newValue,
            sc = {x: Math.max(0, (this.pscroll.x - around.x) * v / u + around.x),
                  y: Math.max(0, (this.pscroll.y - around.y) * v / u + around.y)};
        this.zoom = v;
        this.pscroll = sc;
        this.setZoom(v); //Math.pow(5, (v - 100) / 100));
        this.setScroll(ptround(sc));
    }

    onWheel(ev: WheelEvent) {
        if (ev.ctrlKey) {
            var o = this.areaOffset, r = this.zoomRange,
                xy = {x: o.x - (ev.pageX - this.$el.offsetLeft),
                      y: o.y - (ev.pageY - this.$el.offsetTop)},
                factor = Math.pow(this.accel, -ev.deltaY / 100);
            this.adjustZoom(bounded(this.zoom * factor, r.min, r.max), xy);
            ev.stopPropagation();
            ev.preventDefault();
        }
    }
}


type PointXY = {x: number, y: number};
type FPointXY = PointXY;  /* just to emphasize that it's floats */

function bounded(val: number, min: number, max: number) {
    return Math.max(min, Math.min(max, val));
}

function ptround(p: PointXY) {
    return {x: Math.round(p.x), y: Math.round(p.y)};
}


export { Pan, Zoom }
export type { PointXY, FPointXY }