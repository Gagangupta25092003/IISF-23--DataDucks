import { About } from "./Pages/about";
import { Home } from "./Pages/home";
import { InputDirectory } from "./Pages/input_directory";
import {BrowserRouter as Router , Route, Switch} from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="bg-[#ffffff]">
        <Switch>
        <Route path="/" exact component={About}/>
          <Route path="/database" exact component={Home}/>
          <Route path="/upload_directory" exact component={InputDirectory}/>
        </Switch>
      </div>
    </Router>
  );
}

export default App;


