import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './layouts/Layout';
import { IngestionPage } from './pages/IngestionPage';
import { GraphPage } from './pages/GraphPage';
import { ChatPage } from './pages/ChatPage';
import { LinkagePage } from './pages/LinkagePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<IngestionPage />} />
          <Route path="graph" element={<GraphPage />} />
          <Route path="linkage" element={<LinkagePage />} />
          <Route path="chat" element={<ChatPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
