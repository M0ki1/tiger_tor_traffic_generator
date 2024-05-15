import { Routes, Route} from "react-router-dom";
import { Box } from "@mui/material";
//import Footer from "./components/Footer";
import Sidebar from "./components/Sidebar";
import Home from "./pages/Home";
import Correlations from "./pages/Correlations";
import CorrelationDetails from "./pages/CorrelationDetails";
import Flows from "./pages/Flows";
import Statistics from "./pages/Statistics";
import './App.css';

function App() {
  return (
    <Box sx={{ display: "flex" }}>
      <Sidebar />
      <Box component="main" sx={{ pt: 10, pb: 2, px: 4, width: "100vw" }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/correlations" element={<Correlations />} />
          <Route path="/correlations/:id" element={<CorrelationDetails />} />
          <Route path="/flows" element={<Flows />} />
          <Route path="/statistics" element={<Statistics />} />
        </Routes>
        {/* <Footer />*/} 
      </Box>
    </Box>
  );
}

export default App;
