// Lamentum on the TrimUI Smart Pro: the panel is 1280x720, but the Android player reports 1920x1080
// as the display mode, so the game's resolution menu puts it last and Start() applies it (a 1080p
// render target on a 1 GB device). Replace ManagerMenuPrincipal.ResolucionesCompatibles() with a
// single 1280x720@60 entry.
using Mono.Cecil;
using Mono.Cecil.Cil;

if (args.Length < 2)
{
    Console.Error.WriteLine("usage: resfix <Assembly-CSharp.dll> <out dir>");
    return 2;
}
var managed = Path.GetDirectoryName(Path.GetFullPath(args[0]));
var resolver = new DefaultAssemblyResolver();
resolver.AddSearchDirectory(managed);
var asm = AssemblyDefinition.ReadAssembly(args[0], new ReaderParameters { AssemblyResolver = resolver });
var module = asm.MainModule;

var type = module.Types.FirstOrDefault(t => t.Name == "ManagerMenuPrincipal")
           ?? throw new Exception("ManagerMenuPrincipal not found");
var m = type.Methods.FirstOrDefault(x => x.Name == "ResolucionesCompatibles")
        ?? throw new Exception("ResolucionesCompatibles not found");

var resRef = module.GetTypeReferences().First(t => t.FullName == "UnityEngine.Resolution");
var core = AssemblyDefinition.ReadAssembly(Path.Combine(managed, "UnityEngine.CoreModule.dll"),
                                           new ReaderParameters { AssemblyResolver = resolver });
var resDef = core.MainModule.GetType("UnityEngine.Resolution") ?? throw new Exception("no Resolution");
FieldReference F(string n) => module.ImportReference(resDef.Fields.First(f => f.Name == n));

var body = m.Body;
body.Instructions.Clear();
body.ExceptionHandlers.Clear();
body.Variables.Clear();
var v = new VariableDefinition(module.ImportReference(resRef));
body.Variables.Add(v);
body.InitLocals = true;

var il = body.GetILProcessor();
void Emit(OpCode op) => il.Append(Instruction.Create(op));
void EmitT(OpCode op, TypeReference t) => il.Append(Instruction.Create(op, t));
void EmitF(OpCode op, FieldReference f) => il.Append(Instruction.Create(op, f));
void EmitV(OpCode op, VariableDefinition vv) => il.Append(Instruction.Create(op, vv));
void EmitI(OpCode op, int i) => il.Append(Instruction.Create(op, i));
Emit(OpCodes.Ldc_I4_1);
EmitT(OpCodes.Newarr, module.ImportReference(resRef));
Emit(OpCodes.Dup);
Emit(OpCodes.Ldc_I4_0);
EmitV(OpCodes.Ldloca, v);
EmitT(OpCodes.Initobj, module.ImportReference(resRef));
EmitV(OpCodes.Ldloca, v);
EmitI(OpCodes.Ldc_I4, 1280);
EmitF(OpCodes.Stfld, F("m_Width"));
EmitV(OpCodes.Ldloca, v);
EmitI(OpCodes.Ldc_I4, 720);
EmitF(OpCodes.Stfld, F("m_Height"));
EmitV(OpCodes.Ldloca, v);
il.Append(Instruction.Create(OpCodes.Ldc_I4_S, (sbyte)60));
EmitF(OpCodes.Stfld, F("m_RefreshRate"));
EmitV(OpCodes.Ldloc, v);
EmitT(OpCodes.Stelem_Any, module.ImportReference(resRef));
Emit(OpCodes.Ret);

var outDir = Directory.CreateDirectory(args[1]).FullName;
var outFile = Path.Combine(outDir, Path.GetFileName(args[0]));
asm.Write(outFile);
Console.WriteLine($"rewrote {m.FullName} -> {outFile}");
return 0;
