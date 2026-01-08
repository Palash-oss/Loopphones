
import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  ScanLine, 
  ScrollText, 
  ShoppingBag, 
  Truck, 
  Menu, 
  X,
  Smartphone
} from 'lucide-react';
import { ViewState } from './types';
import { Dashboard } from './components/Dashboard';
import { GradingScanner } from './components/GradingScanner';
import { ProductPassport } from './components/ProductPassport';

const App: React.FC = () => {
  const [activeView, setActiveView] = useState<ViewState>('dashboard');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Telemetry', icon: LayoutDashboard },
    { id: 'scanner', label: 'Grading', icon: ScanLine },
    { id: 'passport', label: 'DPP Registry', icon: ScrollText },
    { id: 'marketplace', label: 'Marketplace', icon: ShoppingBag },
    { id: 'logistics', label: 'Logistics', icon: Truck },
  ];

  const renderView = () => {
    switch (activeView) {
      case 'dashboard': return <Dashboard />;
      case 'scanner': return <GradingScanner />;
      case 'passport': return <ProductPassport />;
      default: return (
        <div className="flex flex-col items-center justify-center h-[60vh] text-gray-500">
          <Smartphone size={64} className="mb-4 opacity-20" />
          <h2 className="text-xl font-bold">Section Under Construction</h2>
          <p>Coming in next sprint of 2026 infrastructure deployment.</p>
        </div>
      );
    }
  };

  return (
    <div className="min-h-screen flex bg-[#0a0a0a] text-gray-100 overflow-x-hidden">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 flex-col glass border-r border-white/5 sticky top-0 h-screen">
        <div className="p-8">
          <div className="flex items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
              <div className="w-4 h-4 border-2 border-black rounded-full"></div>
            </div>
            <h1 className="text-xl font-black italic tracking-tighter">LOOP PHONES</h1>
          </div>
          
          <nav className="space-y-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveView(item.id as ViewState)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${
                  activeView === item.id 
                    ? 'bg-emerald-500 text-black font-bold shadow-lg shadow-emerald-500/20' 
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <item.icon size={20} className={activeView === item.id ? 'text-black' : 'group-hover:scale-110 transition-transform'} />
                {item.label}
              </button>
            ))}
          </nav>
        </div>
        
        <div className="mt-auto p-8">
          <div className="p-4 bg-white/5 rounded-2xl border border-white/10">
            <p className="text-xs text-gray-400 font-bold uppercase tracking-widest mb-1">Circular Goal</p>
            <div className="flex justify-between items-end mb-2">
              <span className="text-xl font-black">82%</span>
              <span className="text-[10px] text-emerald-400">+5% vs LY</span>
            </div>
            <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500 w-[82%]"></div>
            </div>
          </div>
        </div>
      </aside>

      {/* Mobile Nav */}
      <div className="lg:hidden fixed bottom-0 left-0 right-0 z-50 glass border-t border-white/5 px-6 py-4 flex justify-between items-center backdrop-blur-xl">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setActiveView(item.id as ViewState)}
            className={`flex flex-col items-center gap-1 ${activeView === item.id ? 'text-emerald-400' : 'text-gray-500'}`}
          >
            <item.icon size={20} />
            <span className="text-[10px] font-bold uppercase tracking-tighter">{item.label.split(' ')[0]}</span>
          </button>
        ))}
      </div>

      {/* Main Content */}
      <main className="flex-1 p-4 md:p-8 lg:p-12 pb-24 lg:pb-12 max-w-7xl mx-auto w-full">
        {/* Mobile Header */}
        <div className="lg:hidden flex items-center justify-between mb-8">
           <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-emerald-500 rounded-lg flex items-center justify-center">
              <div className="w-4 h-4 border-2 border-black rounded-full"></div>
            </div>
            <h1 className="text-lg font-black italic tracking-tighter">LOOP</h1>
          </div>
          <button onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {renderView()}
      </main>
    </div>
  );
};

export default App;
