class DCLogic {
  constructor(props) { this.props = props || {}; this.state = {}; }
  setState(patch) { Object.assign(this.state, typeof patch === 'function' ? patch(this.state) : patch); if (window.__dcSchedule) window.__dcSchedule(); }
}
window.DCLogic = DCLogic;
