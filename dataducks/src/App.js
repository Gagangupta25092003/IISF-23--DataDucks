import { About } from "./Pages/about";
import { Analytics } from "./Pages/analytics";
import { Home } from "./Pages/home";
import { InputDirectory } from "./Pages/input_directory";
import {BrowserRouter as Router , Route, Switch} from 'react-router-dom';
import MapWithGeoJSON from "./components/Preview_GeoJson";

function App() {
  return (
    <Router>
      <div className="bg-[#ffffff]">
        <Switch>
        <Route path="/" exact component={About}/>
          <Route path="/database" exact component={Home}/>
          <Route path="/upload_directory" exact component={InputDirectory}/>
          <Route path="/analytics" exact component={Analytics}/>
          <Route path="/view-geojson/:geojsonPath" component={MapWithGeoJSON} />
        </Switch>
      </div>
    </Router>
  );
}

export default App;


