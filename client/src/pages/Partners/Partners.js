import React, { Component } from 'react';
import Wrap from '../../components/Wrap/Wrap.js';
import SearchBar from '../../components/SearchBar/SearchBar.js';
import './Partners.scss';
import axios from 'axios';

export default class Partners extends Component {
  constructor(props) {
    super(props);

    this.state = {
      searchResult: {}
    }
  }

  set(obj) {
    this.setState(obj);
  }

  componentDidMount() {
    axios.get('/api/partners')
      .then(res => {
        this.setState({ searchResult: res.data});
      })
      .catch(err => {
        alert("Search failed. Try reloading the page.");
      });
  }

  render () {
    const items = this.state.searchResult ? this.state.searchResult.items : false;

    return (
      <Wrap {...this.props}>
        <h1>Partners</h1>
        <SearchBar
          endpoint="partners"
          set={this.set.bind(this)}
        />
        <br/><br/>
          {items && items.length > 0 ? items.map(({ name, opportunity_count }) => {
            return (
              <div>
                <h4><u>{name}</u></h4>
                <p>{opportunity_count} opportunities</p>
                <div>
                  <span className='badge badge-pill badge-primary'> Children </span>
                  <span className='badge badge-pill badge-primary'> Art </span>
                  <span className='badge badge-pill badge-primary'> Teaching </span>
                  <span className='badge badge-pill badge-primary'> Cooking </span>       
                </div>
                <br/>
              </div>
            );
          }) : <p className="text-danger">No Partners found.</p>}
      </Wrap>
    );
  }
}